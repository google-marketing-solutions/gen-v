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
"""Tests for the config file."""
from unittest import mock


def test_images_uri(mock_app_settings):
  """Tests the images_uri computed field."""
  with mock.patch(
      'gen_v.utils.get_current_week_year_str', return_value='week22-2025'
  ):
    expected_uri = 'my-bucket/my-folder/input-images/week22-2025'
    assert mock_app_settings.images_uri == expected_uri


def test_intros_outros_uri(mock_app_settings):
  """Tests the intros_outros_uri computed field."""
  expected_uri = 'my-bucket/my-folder/input-videos/'
  assert mock_app_settings.intros_outros_uri == expected_uri


def test_audio_uri(mock_app_settings):
  """Tests the audio_uri computed field."""
  expected_uri = 'my-bucket/my-folder/audio/'
  assert mock_app_settings.audio_uri == expected_uri


def test_veo_output_gcs_uri_base(mock_app_settings):
  """Tests the veo_output_gcs_uri_base computed field."""
  expected_uri = 'gs://my-bucket/my-folder/output-videos/veo/'
  assert mock_app_settings.veo_output_gcs_uri_base == expected_uri


def test_video_model_uri(mock_app_settings):
  """Tests the video_model_uri computed field."""
  settings = mock_app_settings
  expected_uri = (
      f'https://{settings.gcp_region}-aiplatform.googleapis.com/v1/'
      f'projects/{settings.gcp_project_id}/locations/{settings.gcp_region}/'
      f'publishers/google/models/{settings.veo_model_name}'
  )
  assert settings.video_model_uri == expected_uri


def test_prediction_endpoint(mock_app_settings):
  """Tests the prediction_endpoint computed field."""
  expected_endpoint = f'{mock_app_settings.video_model_uri}:predictLongRunning'
  assert mock_app_settings.prediction_endpoint == expected_endpoint


def test_fetch_endpoint(mock_app_settings):
  """Tests the fetch_endpoint computed field."""
  expected_endpoint = (
      f'{mock_app_settings.video_model_uri}:fetchPredictOperation'
  )
  assert mock_app_settings.fetch_endpoint == expected_endpoint


def test_selected_prompt_text_custom(mock_app_settings):
  """Tests selected_prompt_text returns the custom prompt."""
  settings = mock_app_settings
  assert settings.selected_prompt_text == settings.custom_video_prompt


def test_selected_prompt_text_gemini(mock_app_settings):
  """Tests selected_prompt_text returns the Gemini prompt."""
  settings = mock_app_settings
  settings.prompt_type = 'GEMINI'
  assert settings.selected_prompt_text == settings.gemini_base_prompt


def test_aspect_ratio_landscape(mock_app_settings):
  """Tests aspect_ratio returns '16:9' for LANDSCAPE."""
  settings = mock_app_settings
  assert settings.aspect_ratio == '16:9'


def test_aspect_ratio_portrait(mock_app_settings):
  """Tests aspect_ratio returns '9:16' for PORTRAIT."""
  settings = mock_app_settings
  settings.video_orientation = 'PORTRAIT'
  assert settings.aspect_ratio == '9:16'


def test_output_file_prefix_landscape(mock_app_settings):
  """Tests output_file_prefix returns correctly for LANDSCAPE."""
  settings = mock_app_settings
  assert settings.output_file_prefix == 'video-landscape'


def test_output_file_prefix_portrait(mock_app_settings):
  """Tests output_file_prefix returns correctly for PORTRAIT."""
  settings = mock_app_settings
  settings.video_orientation = 'PORTRAIT'
  assert settings.output_file_prefix == 'video-portrait'
