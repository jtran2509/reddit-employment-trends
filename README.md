# Comprehensive Market Intelligence Dashboard
![Brain_tumor](brain-tumor-illustrate.jpg)

## 1. Intro to the problem
- A Brain tumor is considered as one of the aggressive diseases, among children and adults. Brain tumors account for 85 to 90 percent of all primary Central Nervous system (CNS) tumors.

- The 5-year survival rate for people with cancerous brain or CNS tumor is approximately 34% for men and 36% for women.

- Brain tumors are classified as: Benign tumor, Malignant Tumor, Pituitary Tumor, etc. Proper treatment, planning, and accurate diagnostics should be implemented to improve the life expectanct of patients.

- The best technique to detect brain tumors is Magnetic Resonance Imaging (MRI). A huge amount of image data is generated through the scans. These images are examined by radiologists. A manual examination can be error-prone due to the level of complexities involved in brain tumors and their properties.

- A brain tumor is considered one of the most aggressive diseases, among children and adults. With manual examination, it can be error-prone due to the level of complexity. Hence, adding Machine Learning (ML) and Artificial intelligence (AI) has consistently shown higher accuracy than manual classification.

## 2. Project Structure
- data_utiles.py: 
- models.py: Defined 1-layer, 6-layer, Resnet18 and VGG16 architectures adapted for 1-channel MRI in put
- scrape_reddit.py: Scraping data from Reddit page with 2800 posts from various subreddits about job market in Canada, immigrants' situation and their thoughts/obstacles/ways to navigate through the foreign life

## 3. Potential Impact
**Filter out pain points**: pointed out what the main concenrs/worries of the immigrants as well as those who have been living in Canada for a long time, their thoughts on job market as of 2026 (e.g. work permit, degrees, racial discrimination still happens?)

**Sentimental Analysis**: immigrants & job seekers attitudes towards the job market (positive or negative)? How can the recruiters using this to adapt to their hiring policies?

**REAL-TIME trend**: the dashboard will show the recruiters which job category is on the hot search now? Are there any new policies being adapted that stirs the community

**Finding skills gap**: Overview of the skills/certificate that are "hot", popolar, mostly-spoken about right now => Purpose: recruiters can use it to see the trend in job market and adjust their job description, users will be able to know what skills to update themselves on.

## 4. Data Source:
- Dataset: This dataset contains 2800 posts of over 10 subreddit categories ("VietNam", "Calgary", "askTO", "asianamerican", "CanadaJobs", "povertyfinancecanada", "Layoffs", "antiwork", "ImmigrationCanada", "LMIASCAMS", "OntarioColleges", "cscareerquestionsCAD", "VancouverJobs", "canadahousing")

# Dashboard Preview

## Overview
**Interactive Dashboard**: 
1. Tab 1: Market pulse
- Top 20 keywords after scraping reddit post every monday (showing results from last week) at 9AM
- LMIA: Lmia is always the hottest topic with more negative feelings towards it (more policies are created and immigrants have to keep track and update themselves as soon as possible) 

2. Tab 2: Technical Skills vs Reality
- Sentimental chart between different, in this case programming languages

3. Tab 3: Multilingual Community 
- Statistics from `langdetect`: 98% of the reddit posts are written in English, some of them are in other languages (e.g. Vietnamese, Korean, Japanese). Therefore, we can see that most immigrants are trying to incooporate English into their post for navigating through the community and settling down, while some are still keeping their cultures with post in their native languages.

## How to Run:
- Make sure you have PyTorch and necessary libraries installed. 
- Follow the steps outlined in the notebook, from data loading to model evaluation. After the first few tries, feel free to experiment different parameters. 

## Key Components:
1. Data Loading and Preprocessing: 
During the data processing, we use `Spacy` library for tokenization and lemmatization,  and `langdetect` to divide the dataset into Vietnamese and English-posts
2. 
3. Training:
Splitting training and testing dataset at 9:1 ratio and run through different number of epochs to test the efficiency.
4. Evaluation
Evaluate each model on the validation set. 
  
## Technologies Used:
[Python](https://en.wikipedia.org/wiki/Python_(programming_language))
[PyTorch](https://pytorch.org/)
[Pandas](https://en.wikipedia.org/wiki/PANDAS)
[Scikit-learn](https://scikit-learn.org/stable/)
[Grad-CAM](https://github.com/jacobgil/pytorch-grad-cam)
[MONAI](https://github.com/Project-MONAI/MONAI)
[VGG16](https://keras.io/api/applications/vgg/)
[Resnet18](https://docs.pytorch.org/vision/main/models/generated/torchvision.models.resnet18.html)

## Model Accuracy Results:

The table below will display various accuracy achieved by diffrent models:

## Next Steps for Model Improvement
To further enhance the performance and capabilities as well as practicality of the CNN model, the following steps are recommended:
1. Model refinement
- Data input: The more data coming in, the better the model will be trained and learn different patterns of MRI. Currently, the model is being trained on a limited dataset, hence, the performance will somehow be limited
- Hyperparameter tuning: higher epochs don't necessary guarantee better performance, looking into playing with batch sizes, learning rates, etc. might give better performance



  
## Contact
| Contact Method | |
| --- | --- |
| Professional Email | dungvn1999@gmail.com |
| LinkedIn | https://www.linkedin.com/in/dungtran99/ |
| Project Link | [https://github.com/jtran2509/brain_tumor]() |

