Copyright 2025 Google LLC

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    https://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

![Gen V logo](./docs/images/gen-v-logo-small.png)

# Disclaimer

Gen V is NOT an official Google product.

# Gen V: AI-Powered Video Ads

Create AI-powered video ads with [Veo](
https://deepmind.google/technologies/veo/veo-2/) on Google Cloud, enhanced with
AI voice and audio, and personalised with brand logos, stickers and promo texts.

# Gen V Colab fka Feedflix

Our initial use case, is implemented as a user-friendly Colab notebook.
This Colab notebook demonstrates how to use Google's Generative AI models 
(Gemini and Video Generation) to create short video ads from product images.

## Gen V Colab features 

* **Image Processing:** Resizes and recolors product images to prepare them for video generation.
* **Prompt Generation:** Uses Gemini to analyze images and generate creative video prompts.
* **Video Generation:** Leverages Google's Video Generation API to create short video ads from images and prompts.
* **User Selection:** Allows users to interactively choose the best-generated videos.
* **Video Editing:** Enables adding overlays, transitions, and audio to enhance the final video.
* **Video Stitching:** Combines selected videos into a single, cohesive advertisement.

## Getting Started

1. **Open the Colab notebook:** See section below "How to start with the Colab"
2. **Set up your GCP project:**
    * Enable the required APIs: Gemini, Cloud Storage. See section below called "Requirements" 
    * Create a Cloud Storage bucket to store your input and output files. See section below: "GCS Assets Requirements".
    * Update the GCP parameters in the notebook with your project ID, bucket name, and folder name. 
    * Review and if needed update the rest of the parameters in the Colab. See section  below: Customization.
3. **Run the notebook:** Follow the instructions in the notebook to execute the code cells and generate your video ads.
    * Run all cells up to Part1
    * Move to step 4. before running Part1, this creates the required folders in your GCS storage folder.
    * Run cell Part 1 and Part 2:
      * In Part 1, select the Veo generated videos you like per image uploaded. Optionally add promo text if you want to use text overlays.
      * In Part 2, select all the videos you want to be stiched together, intro, veos and outro. Ordering of veos is alphabetical, make sure your input images are alphabetically ordered as your desired Veos order. 
4. **Upload your product images:** Upload your product images to the designated folder in your GCS Storage folder.
    * Make sure you upload the images in the input-images/weekXX-YYYY folder which was just created with the Colab

### How to start with the Colab

1. Navigate to [colab.research.google.com](http://Colab.research.google.com).
2. In the dialog, open a Notebook from GitHub.
3. Enter the url from this page.

### Requirements

* Google Cloud Project with billing enabled.
* Enabled APIs:
    * [Vertex AI API](https://console.cloud.google.com/marketplace/product/google/aiplatform.googleapis.com)
    * [Cloud Storage API](https://console.cloud.google.com/marketplace/product/google/storage.googleapis.com)
* Python 3.7 or later.
* Required Python libraries: `google-genai`, `mediapy`, `Pillow`, `moviepy`.
  
### GCS Assets Requirements

1. Store your assets on [Google Cloud Storage](https://console.cloud.google.com/storage/browser) with the following folder structure:
    * **[GCP_BUCKET_NAME]** - name of bucket, ensure you have write permission.
    * **[FOLDER_NAME]** - name of the folder in the bucket, ensure you have write permission.
    * When you execute the initial cells of the Colab notebook within the designated folder, six subfolders will be generated:
        * **audio** - (Required, exactly one file) Add in the folder your m4a audio file with the background music. 
        * **fonts** - (Required, exactly one file named font.ttf). Add here your .otf or .ttf font file. If .otf, you need to update that in the Colab parameters.
        * **input-images** - Add your product images here, in the correct sub-folder named weekXX-YYYY which is the same week number XX as you are running the Colab.
        * **input-overlays** - (Required, exactly one file name sticker.png) Add here your sticker.png if you want to use sticker overlay. If not, you have to remove it from the Colab by sending empty list (e.g.[]) instead of GCS_IMAGES_TEST or remove the logo and/or the sticker from the variable in the parameters.
        * **input-videos** - (Required, exactly two files named intro_clip.mp4 and outro_clip.mp4). Add here your intro and outro videos that you want appedend before and after the Veo generated videos. If you don't want to use them, you can leave them un-checked in the Part2 of the Colab.
        * **logos** - (Required, exactly one file name logo.png) Add here your logo if you want to use a logo overlay, ideally in small dimensions with high quality resolution. If not, you have to remove it from the Colab.

### Customization

* **Video Prompts:** You can [customize the video prompts](https://cloud.google.com/vertex-ai/generative-ai/docs/video/video-gen-prompt-guide) used by the Video Generation API.
* **Video Parameters:** Adjust the duration, sample count (default 2, maximum 4), and other parameters to control the generated videos.
* **Overlays and Transitions:** Add your own logos, stickers, text overlays, and transitions to personalize your videos.
* **Audio:** Include background music to enhance the audio experience. Voice overs are not supported yet. The Colab outputs 2 variations of the final video, one with and one without audio.

### Colab Troubleshooting

* Some steps do not produce output, they only define functions.
* If a step asks you to **Restart Runtime**, do so.
* Steps Part1 and Part2 require user selection so "Run all cells" **will not** produce an end to end succesful run without stopping for user selection
* Make sure you re-run the GCP Parameters cell, if you are modifying any of the parameters.  
* If a step displays an error, stop and debug it. Debug the following:
  * APIs are enabled.
  * Storage bucket is correctly configured and the files are present with the same names the Colab expects (e.g. font.ttf) or rename the defaults in the Colab
  * Previous Colab sections completed and user selection was done.
  * If error mentions 'Response' it may be due to Veo timing out or not providing a response, for reasons like:
      * Large input image, aim for images with size less than 20MB.
      * Image could potentially contain sensitive information e.g. a person can be mistakenly identified as a child. Read more [here](https://cloud.google.com/vertex-ai/generative-ai/docs/video/generate-videos)
  * Select _Runtime > Reset Session and Run All_ as a last resort.

### Output

The output is **not** visualized at the end of the Colab as it is only saved in the GCS Storage.

Wait for the following text printed at the end of the Colab: "Uploaded file to: gs://[GCP_BUCKET_NAME]/[FOLDER_NAME]/output-videos/concatenated/weekXX-YYYY/video_transition_demo.mp4" before you check the GCS storage folder.

In the GCS Storage Folder **output-videos** there are 4 sub-folders created:

* **veo** - Contains all the latest Veo video generated, in a weekXX-YYYY folder, per input image.
* **image-overlays** - Contains all the Veo videos overlayed with image overlay (logo and/or sticker), if passed in the Colab.
* **final-overlays** - Contains all the Veo videos overlayed with images and text, if passed in the Colab part 1. 
* **concatenated** - Contains two final output videos of: intro, veos and outro concatenated together, one with and one without an audio.
    

## Disclaimer

> **Note:** This solution uses AI to edit or generate assets for your ads. Whether your content requires labeling depends on the nature of your assets, where your ads serve, and specific legal obligations that apply to you. In some circumstances Google may automatically apply a label. Please consult with your legal team to determine if/when a label is required for your ads. You can add labels in Google’s Ads products using the [AI label setting](https://support.google.com/google-ads/answer/17140115).

This is a sample Colab notebook and may require modifications to suit your specific needs.

This is not an officially supported Google product.

Copyright 2025 Google LLC. This solution, including any related sample code or data, is made available on an "as is", "as available", and "with all faults" basis, solely for illustrative purposes, and without warranty or representation of any kind. This solution is experimental, unsupported and provided solely for your convenience. Your use of it is subject to your agreements with Google, as applicable, and may constitute a beta feature as defined under those agreements. To the extent that you make any data available to Google in connection with your use of the solution, you represent and warrant that you have all necessary and appropriate rights, consents and permissions to permit Google to use and process that data. By using any portion of this solution, you acknowledge, assume and accept all risks, known and unknown, associated with its usage, including with respect to your deployment of any portion of this solution in your systems, or usage in connection with your business, if at all.
