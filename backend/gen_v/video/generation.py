# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Functions for generating video content using Google Cloud AI APIs.

This module handles interactions with services like Vertex AI Gemini for prompt
generation and the Video Generation API for creating video clips from images and
prompts.
"""
import concurrent.futures
from datetime import date
import functools
import logging
import sys
import time

from google import genai
import google.auth
from google.auth.transport import requests as google_requests
from google.cloud import storage as gcp_storage
from google.genai import types
import requests

from gen_v import config
from gen_v import models
from gen_v import storage
from gen_v import utils


logging.basicConfig(stream=sys.stdout)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def get_access_token() -> str:
  """Retrieves the access token for the currently active account."""
  creds, _ = google.auth.default()
  if not creds.valid:
    creds.refresh(google_requests.Request())
  return creds.token


def send_request_to_google_api(
    api_endpoint: str,
    data: dict[str, any] = None,
    access_token: str | None = None,
    timeout: int = 60,
) -> dict[str, any]:
  """Sends an HTTP request to a Google API endpoint.

  Args:
    api_endpoint: The URL of the Google API endpoint.
    data: (Optional) Dictionary of data to send in the request body.
    access_token: The access token to use for authentication. If not provided,
      the default credentials will be used. This is primarily used for
      dependency injection in testing.
    timeout: The number of seconds before giving up the request.

  Returns:
    The response from the Google API.

  Raises:
    requests.exceptions.HTTPError: If the API request fails (non-2xx status
    code).
  """
  if access_token is None:
    access_token = get_access_token()

  headers = {
      'Authorization': f'Bearer {access_token}',
      'Content-Type': 'application/json',
  }

  response = requests.post(
      api_endpoint, headers=headers, json=data, timeout=timeout
  )
  response.raise_for_status()
  return response.json()


def get_gemini_generated_video_prompt(
    request_data: models.GeminiPromptRequest,
    project_id: str = None,
    location: str = None,
    client: genai.Client | None = None,
) -> str | None:
  """Uses Gemini to analyse an image and generate a video prompt.

  Args:
    request_data: A GeminiPromptRequest object containing input file, prompt
      text, and model name.
    project_id: The project ID to use in the client.
    location: The Google Cloud location to use in the client.
    client: For dependency injection, provide a client to use. If not used, one
      will be created using the project_id and location.

  Returns:
      The generated video prompt as a string, or None if there was an error.

  Raises:
    ValueError if client is None and a project_id and location aren't provided.
  """
  if client is None:
    if not project_id or not location:
      raise ValueError(
          'project_id and location must be provided if client is None'
      )
    client = genai.Client(vertexai=True, project=project_id, location=location)

  contents = [request_data.prompt_text]
  if request_data.image_bytes and request_data.mime_type:
    contents.append(
        types.Part.from_bytes(
            data=request_data.image_bytes, mime_type=request_data.mime_type
        )
    )
  else:
    logger.warning('No image found, sending only the prompt.')

  response = client.models.generate_content(
      model=request_data.model_name,
      contents=contents,
      config=types.GenerateContentConfig(
          media_resolution=types.MediaResolution.MEDIA_RESOLUTION_LOW,
      ),
  )
  logger.info('The response is: %s', response.text)
  return response.text


def fetch_operation(lro_name: str, settings: config.AppSettings) -> str | None:
  """Fetches the status of a long-running operation.

  Makes regular pings to the API endpoint to determine the status of the job. It
  usually takes about 2 mins to generate a request. This function will give up
  after 30 loops (5 mins).

  Args:
    lro_name: The name of the long-running operation.
    settings: An instance of AppSettings containing configuration, including
      the derived fetch_endpoint.

  Returns:
    The response from the API containing the operation status.

  """
  request = {'operationName': lro_name}
  # The generation usually takes 2 minutes. Loop 30 times, around 5 minutes.
  max_attempts = 30
  attempt_interval = 10

  for _ in range(max_attempts):
    try:
      resp = send_request_to_google_api(settings.fetch_endpoint, request)
      if 'done' in resp and resp['done']:
        return resp
    except requests.exceptions.HTTPError as e:
      logger.error('Error while fetching operation: %s', e)

    time.sleep(attempt_interval)


def image_to_video(
    veo_request: models.VeoApiRequest,
    settings: config.AppSettings,
) -> str | None:
  """Generates a video from an image using the Video Generation API.

  Args:
    veo_request: The request model to Veo containing information such as the
      prompt.
    settings: An instance of AppSettings containing configuration, including
      the derived fetch_endpoint.

  Returns:
    A dictionary containing the response from the Video Generation API,
    including the operation details and generated video information.

  """
  request_payload = veo_request.to_api_payload()
  logger.info('Making image to video request with this payload')
  logger.info(request_payload)

  try:
    resp = send_request_to_google_api(
        settings.prediction_endpoint, request_payload
    )
    return fetch_operation(resp['name'], settings)
  except requests.exceptions.HTTPError as e:
    logger.error('Error sending image_to_video request: %s', e)


def generate_videos_and_download(
    veo_request: models.VeoApiRequest,
    settings: config.AppSettings,
    output_file_prefix: str,
    product: dict[str, any],
    storage_client: gcp_storage.Client = None,
) -> list[dict[str, any]]:
  """Generates videos, downloads them, and returns their information.

  Args:
    veo_request: The request model to Veo containing information such as the
    prompt.
    settings: An instance of AppSettings containing configuration, including
    the derived fetch_endpoint.
    output_file_prefix: The prefix for output video file names.
    product: A dictionary containing product information.

  Returns:
    A list of dictionaries, containing information about a generated video
  """
  output_videos = image_to_video(veo_request, settings)
  file_name = storage.get_file_name_from_gcs_url(veo_request.image_uri)

  output_video_files = []
  logger.info(
      'Generated videos %s for %s',
      len(output_videos['response']['videos']),
      file_name,
  )

  for video in output_videos['response']['videos']:
    veo_name = storage.get_file_name_from_gcs_url(video['gcsUri'])
    output_video_local_path = f'{file_name}-{output_file_prefix}-{veo_name}'

    storage.download_file_locally(video['gcsUri'], output_video_local_path)

    video_uri = storage.move_blob(
        video['gcsUri'], file_name, storage_client=storage_client
    )

    output_video_files.append({
        'gcs_uri': video_uri,
        'local_file': output_video_local_path,
        'local_file_name': output_video_local_path.rsplit('/', maxsplit=1)[-1],
        'product_title': product['title'],
        'promo_text': '',
    })

  return output_video_files


def generate_video_for_item(
    item_data: dict, settings: config.AppSettings
) -> list[dict]:
  """Generates video(s) for a single item/entity based on configuration.

  Args:
    item_data: A dictionary containing data about the item.
      Expected keys: 'recolored_image_uri'
    settings: An instance of AppSettings containing configuration, including
      the derived fetch_endpoint.

  Returns:
    A list of dictionaries containing information about the generated video(s),
      or an empty list if an error occurs during generation for this item.
  """
  if 'recolored_image_uri' not in item_data:
    logger.warning(
        "Skipping item due to missing 'recolored_image_uri': %s", item_data
    )
    return []

  recolored_image_uri = item_data['recolored_image_uri']
  logger.info('Processing item: %s', recolored_image_uri)

  recolored_image_local_path = storage.download_file_locally(
      recolored_image_uri
  )

  base_prompt_text = settings.selected_prompt_text

  final_prompt = ''
  if settings.prompt_type == 'CUSTOM':
    final_prompt = base_prompt_text
  elif settings.prompt_type == 'GEMINI':
    gemini_prompt_request = models.GeminiPromptRequest(
        prompt_text=base_prompt_text,
        image_file_path=recolored_image_local_path,
        model_name=settings.gemini_model_name,
    )
    final_prompt = get_gemini_generated_video_prompt(
        gemini_prompt_request,
        project_id=settings.gcp_project_id,
        location=settings.gcp_region,
    )
  else:
    logger.error('Invalid prompt type: %s', settings.prompt_type)

  logger.debug(
      'Running prompt "%s" for aspect ratio "%s", and orientation "%s"',
      final_prompt,
      settings.aspect_ratio,
      settings.video_orientation,
  )

  output_gcs_uri = settings.veo_output_gcs_uri_base
  if settings.veo_add_date_to_output_path:
    date_component = utils.get_current_week_year_str(date.today())
    output_gcs_uri += f'{date_component}/'

  veo_request = models.VeoApiRequest(
      prompt=final_prompt,
      image_uri=recolored_image_uri,
      gcs_uri=output_gcs_uri,
      duration=settings.veo_duration_seconds,
      sample_count=settings.veo_sample_count,
      aspect_ratio=settings.aspect_ratio,
      negative_prompt=settings.veo_negative_prompt,
      prompt_enhance=settings.veo_prompt_enhance,
      person_generation=settings.veo_person_generation,
  )
  generated_videos = generate_videos_and_download(
      veo_request=veo_request,
      settings=settings,
      output_file_prefix=settings.output_file_prefix,
      product=item_data,
  )
  logging.info(
      'Successfully generated %d video(s) for item: %s',
      len(generated_videos),
      recolored_image_uri,
  )
  return generated_videos


def generate_videos_concurrently(
    items_to_process: list[dict], settings: config.AppSettings
) -> list[dict]:
  """Generates videos for a list of items/entities concurrently.

  Args:
    items_to_process: A list of dictionaries, each containing data for an item.
      Each dictionary is passed to generate_video_for_item.
    settings: An instance of AppSettings containing configuration, including
      the derived fetch_endpoint.

  Returns:
    A flat list containing dictionaries of all successfully generated video
      information from all items.
  """
  logger.info(
      'Starting concurrent video generation for %d items.',
      len(items_to_process),
  )
  all_generated_videos = []

  worker_func = functools.partial(generate_video_for_item, settings=settings)

  with concurrent.futures.ThreadPoolExecutor() as executor:
    results_iterator = executor.map(worker_func, items_to_process)
    for video_list in results_iterator:
      if video_list:
        all_generated_videos.extend(video_list)
  logger.info(
      'Finished concurrent video generation. Total videos generated: %d',
      len(all_generated_videos),
  )
  return all_generated_videos


def generate_videos(
    output_uri_path: str,
    resized_image_width: int,
    resized_image_height: int,
    original_background_color: models.RGBColor,
    background_color: models.RGBColor,
    settings: config.AppSettings,
) -> list[dict]:
  """Generates videos from images.

  This function performs the following steps:
  1. Resizes input images into landscape and portrait formats.
  2. Recolors the background of the resized images.
  3. Generates videos (VEOs) from the recolored images.

  Args:
      output_uri_path: The GCS URI of the folder where output will be stored.
      resized_image_width: The desired width of the resized images.
      resized_image_height: The desired height of the resized images.
      original_background_color: The original background color of the images.
      background_color: The desired background color of the images.
      settings: An instance of AppSettings containing configuration, including
                the derived fetch_endpoint.

  Returns:
      A list of dictionaries with information about a selected video.
  """
  selected_products = utils.process_and_resize_images(
      settings.images_uri,
      resized_image_width,
      resized_image_height,
      original_background_color,
      output_uri_path,
  )
  utils.recolor_background_and_upload(
      selected_products,
      output_uri_path,
      original_background_color,
      background_color,
  )
  output_video_files = generate_videos_concurrently(selected_products, settings)
  return output_video_files
