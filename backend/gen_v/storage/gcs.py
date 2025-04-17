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

"""Functions to interact with Cloud storage"""

import os

from google.cloud import storage


def get_blob(uri: str, storage_client: storage.Client = None) -> any:
  """Returns a Google Cloud Storage blob object from a full URI.

  Args:
    uri: The full Google Cloud Storage URI of the blob to retrieve.
    storage_client: The Google Cloud Storage client.

  Returns:
    A Google Cloud Storage blob object.
  """
  storage_client = storage_client or storage.Client()
  bucket = get_bucket_name_from_gcs_url(uri)
  path = get_path_from_gcs_url(uri)
  return storage_client.bucket(bucket).blob(path)


def download_file_locally(
    uri: str,
    file_name: str = None,
    tmp_string: str = "/content",
    storage_client: storage.Client = None,
) -> str:
  """Downloads a file from Google Cloud Storage to the local file system.

  Args:
    uri: The Google Cloud Storage URI of the file to download.
    file_name: (Optional) The name to give the downloaded file. If not
      provided, the file name will be extracted from the URI.
    tmp_string: (Optional) The directory the download should be placed in.
    storage_client: The Google Cloud Storage client.


  Returns:
    The path to the local file where the file was saved.

  Raises:
    FileNotFoundError: If the file at the given URI does not exist.
  """
  storage_client = storage_client or storage.Client()
  blob = get_blob(uri, storage_client)
  if not blob:
    raise FileNotFoundError(f"File not found at URI: {uri}")
  if not file_name:
    file_name = get_file_name_from_gcs_url(uri)
  if tmp_string not in file_name:
    local_file_path = f"{tmp_string}/{file_name}"
  else:
    local_file_path = file_name

  blob.download_to_filename(local_file_path)
  return local_file_path


def download_files(gcs_uris: list[str]) -> list[str]:
  """Downloads files from Google Cloud Storage to the local file system.

  Args:
    gcs_uris: A list of Google Cloud Storage URIs of the files to download.

  Returns:
    A list of local file paths where the files were saved.
  """
  local_file_paths = []
  for gcs_uri in gcs_uris:
    local_file_paths.append(download_file_locally(gcs_uri))
  return local_file_paths


def retrieve_all_files_from_gcs_folder(
    gcs_uri: str, storage_client: storage.Client = None
) -> list[str]:
  """Retrieve all files from a GCS folder.
  Args:
      gcs_uri: The GCS folder to retrieve files from.
      storage_client: The Google Cloud Storage client.
  Returns:
      A list of GCS URIs for all files in the folder.
  """
  storage_client = storage_client or storage.Client()
  bucket_name = get_bucket_name_from_gcs_url(gcs_uri)
  bucket = storage_client.bucket(bucket_name)

  path = get_path_from_gcs_url(gcs_uri)

  blobs = bucket.list_blobs(prefix=path)
  output = []
  for blob in blobs:
    if len(blob.name.split(".")) > 1:
      output.append(f"gs://{bucket_name}/{blob.name}")
  return output


def upload_file_to_gcs(
    local_file_path: str, gcs_uri: str, storage_client: storage.Client = None
) -> None:
  """Upload a file to GCS

  Args:
      local_file_path: The local system path to the file to upload.
      gcs_uri: The GCS URI where the file should be uploaded.
      storage_client: The Google Cloud Storage client.
  """
  storage_client = storage_client or storage.Client()
  try:
    bucket_name = get_bucket_name_from_gcs_url(gcs_uri)
    bucket = storage_client.bucket(bucket_name)
    subdirectory_path = get_path_from_gcs_url(gcs_uri)

    output_blob = bucket.blob(subdirectory_path)
    output_blob.upload_from_filename(
        filename=local_file_path, client=storage_client
    )
    print(f"Uploaded file to: {gcs_uri}")
    os.remove(local_file_path)
  except OSError as e:
    print(f"Unable to remove local copy of uploaded file: {e}")
  except storage.exceptions.InvalidResponse as e:
    print(f"Error in upload_file_to_gcs: {e}")
    print(f"Can not upload file: {local_file_path}")
    print(f"to gcs_uri: {gcs_uri}")
  except storage.exceptions.DataCorruption as e:
    print(f"Error in upload_file_to_gcs: {e}")
    print(f"Can not upload file: {local_file_path}")
    print(f"to gcs_uri: {gcs_uri}")


def get_file_name_from_gcs_url(gcs_uri: str) -> str:
  """Get file name from GCS url
  Args:
      gcs_uri: the gcs url with the file name
  Returns:
      The file name with its format
  """
  return gcs_uri.split("/")[-1]


def get_bucket_name_from_gcs_url(gcs_uri: str) -> str:
  """Get bucket name from GCS url
  Args:
      gcs_uri: the gcs url with the bucket name
  Returns:
      The bucket name
  """
  return gcs_uri.replace("gs://", "").split("/")[0]


def get_path_from_gcs_url(gcs_uri: str) -> str:
  """Get path from GCS url
  Args:
      gcs_uri: the gcs url with the path
  Returns:
      The path
  """
  return "/".join(gcs_uri.replace("gs://", "").split("/")[1:])


def create_gcs_folders_in_subfolder(bucket_name, subfolder_name, folder_names):
    """Creates folders within a subfolder in a Google Cloud Storage bucket.
    Skips folder creation if the folder already exists.

    Args:
        bucket_name: The name of the bucket.
        subfolder_name: The name of the subfolder.
        folder_names: A list of folder names to create within the subfolder.
    """
    storage_client = storage.Client()
    bucket = storage_client.bucket(bucket_name)

    for folder_name in folder_names:
        folder_path = f"{subfolder_name}/{folder_name}/"
        blob = bucket.blob(folder_path)

        if not blob.exists():  # Check if folder already exists
            blob.upload_from_string('')  # Create folder if it doesn't exist
            print(f"Folder '{folder_name}' created within subfolder '{subfolder_name}' in bucket '{bucket_name}'.")
