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
"""Configuration settings for the video generation backend.

This module defines the application settings using Pydantic, loading values
from environment variables or using sensible defaults. It centralizes
configuration related to Google Cloud Platform resources, storage paths,
and temporary directories.
"""
from typing import Literal
import pydantic
import pydantic_settings

from gen_v import utils


class AppSettings(pydantic_settings.BaseSettings):
  """The settings used in the application.

  Attributes:
    gcp_project_id: Google Cloud Project ID.
    gcp_bucket_name: Google Cloud Storage bucket name.
    gcs_folder_name: Base folder name within the GCS bucket.
    gcp_region: The Google Cloud region to use.
    veo_model_name: The name of the Veo model to use for video generation.
    veo_duration_seconds: Default duration for generated VEO clips.
    veo_sample_count: Default number of samples for VEO generation.
    veo_negative_prompt: Default negative prompt for VEO generation.
    veo_prompt_enhance: Default setting for VEO prompt enhancement.
    veo_person_generation: Default setting for VEO person generation.
    veo_add_date_to_output_path: If True, appends '/weekY-YYYY' to the base
      output path.
    gemini_model_name: The name of the Gemini model used for prompt generation.
    prompt_type: The method for generating video prompts ('CUSTOM' or 'GEMINI').
    custom_video_prompt: The prompt text to use when prompt_type is 'CUSTOM'.
    gemini_base_prompt: The base prompt text passed to Gemini when
      prompt_type is 'GEMINI'.
    video_orientation: The desired aspect ratio orientation
      ('LANDSCAPE' or 'PORTRAIT').
  """

  gcp_project_id: str
  gcp_bucket_name: str
  gcs_folder_name: str
  gcp_region: str = "us-central1"

  # Veo settings
  veo_model_name: str = "veo-2.0-generate-001"
  veo_duration_seconds: int = 5
  veo_sample_count: int = 2
  veo_negative_prompt: str = "copyrighted content"
  veo_prompt_enhance: bool = True
  veo_person_generation: Literal["allow_adult", "dont_allow"] = "allow_adult"
  veo_add_date_to_output_path: bool = True

  # Gemini settings
  gemini_model_name: str = "gemini-2.0-flash"

  # Prompt generation settings
  prompt_type: Literal["CUSTOM", "GEMINI"] = "CUSTOM"
  custom_video_prompt: str = (
      "Animate this image in a way that is most appropriate for the content in "
      "the image"
  )
  gemini_base_prompt: str = (
      "Analyse the image and write a prompt for a generative video AI to"
      " animate the video in the most appropriate way for the content to be"
      " displayed in an online ad.  Consider the function of the main object in"
      " the image when deciding how to animate it. If there is a background,"
      " focus on animating the primary object only. Output the prompt only."
      " Don't show any of the analysis or headings in your response, only"
      " provide the prompt you created."
  )

  # Video format settings
  video_orientation: Literal["LANDSCAPE", "PORTRAIT"] = "LANDSCAPE"

  @pydantic.computed_field(return_type=str)
  @property
  def images_uri(self) -> str:
    """Returns the GCS URI for input images."""
    return (
        f"{self.gcp_bucket_name}/{self.gcs_folder_name}/"
        f"input-images/{utils.get_current_week_year_str()}"
    )

  @pydantic.computed_field(return_type=str)
  @property
  def intros_outros_uri(self) -> str:
    """Returns the GCS URI for intros and outros."""
    return f"{self.gcp_bucket_name}/{self.gcs_folder_name}/input-videos/"

  @pydantic.computed_field(return_type=str)
  @property
  def audio_uri(self) -> str:
    """Returns the GCS URI for audio files."""
    return f"{self.gcp_bucket_name}/{self.gcs_folder_name}/audio/"

  @pydantic.computed_field(return_type=str)
  @property
  def video_model_uri(self) -> str:
    """Returns the video model URI."""
    return (
        f"https://{self.gcp_region}-aiplatform.googleapis.com/v1/"
        f"projects/{self.gcp_project_id}/locations/{self.gcp_region}/"
        f"publishers/google/models/{self.veo_model_name}"
    )

  @pydantic.computed_field(return_type=str)
  @property
  def prediction_endpoint(self) -> str:
    """Returns the prediction endpoint for the video model."""
    return f"{self.video_model_uri}:predictLongRunning"

  @pydantic.computed_field(return_type=str)
  @property
  def fetch_endpoint(self) -> str:
    """Returns the fetch endpoint for the video model."""
    return f"{self.video_model_uri}:fetchPredictOperation"

  @pydantic.computed_field(return_type=str)
  @property
  def veo_output_gcs_uri_base(self) -> str:
    """Calculates the base GCS URI for VEO outputs."""
    return (
        f"gs://{self.gcp_bucket_name}/{self.gcs_folder_name}/output-videos/veo/"
    )

  @pydantic.computed_field(return_type=str)
  @property
  def selected_prompt_text(self) -> str:
    """Returns the appropriate base prompt text based on prompt_type."""
    if self.prompt_type == "CUSTOM":
      return self.custom_video_prompt
    return self.gemini_base_prompt

  @pydantic.computed_field(return_type=str)
  @property
  def aspect_ratio(self) -> str:
    """Returns the aspect ratio string based on video_orientation."""
    if self.video_orientation == "PORTRAIT":
      return "9:16"
    return "16:9"

  @pydantic.computed_field(return_type=str)
  @property
  def output_file_prefix(self) -> str:
    """Returns the output file prefix based on video_orientation."""
    if self.video_orientation == "PORTRAIT":
      return "video-portrait"
    return "video-landscape"
