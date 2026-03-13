# 🖼️ AWS Rekognition Image Labeler

> Detect and label objects in images using **Amazon Rekognition**, **S3**, and **Python** — with bounding boxes and confidence scores rendered in real time.

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=flat-square&logo=python)
![AWS](https://img.shields.io/badge/AWS-Rekognition-orange?style=flat-square&logo=amazon-aws)
![boto3](https://img.shields.io/badge/boto3-1.34.0-yellow?style=flat-square)
![License](https://img.shields.io/badge/License-MIT-green?style=flat-square)

---

## 📌 Overview

This project demonstrates how to build an **image label detection system** on AWS using Amazon Rekognition. Images stored in an S3 bucket are analysed by Rekognition, which identifies objects and scenes, returning their labels, confidence scores, and bounding box coordinates. The results are then visualised using Python and Matplotlib.

**Example output:**

![Demo output showing bounding boxes around detected objects like Person, Shoe, Shorts with 99%+ confidence]

---

## 🏗️ Architecture

```
┌─────────────┐     Upload      ┌──────────────┐    detect_labels    ┌──────────────────────┐
│  Local Image │ ─────────────► │  Amazon S3   │ ──────────────────► │  Amazon Rekognition  │
└─────────────┘                 └──────────────┘                     └──────────────────────┘
                                        ▲                                        │
                                        │                                        │ Labels +
                                   boto3 SDK                               Confidence Scores +
                                        │                                  Bounding Boxes
                                ┌───────────────┐                               │
                                │  Python Script │ ◄─────────────────────────────┘
                                │  (app.py)      │
                                └───────────────┘
                                        │
                                        ▼
                                ┌───────────────┐
                                │  Matplotlib   │
                                │  Visualiser   │
                                └───────────────┘
```

**AWS Services Used:**

| Service | Purpose |
|---|---|
| Amazon S3 | Stores the images to be analysed |
| Amazon Rekognition | Analyses images and returns labels with confidence scores |
| AWS IAM | Provides least-privilege access for CLI authentication |
| AWS CLI | Authenticates and interacts with AWS services locally |

---

## ✨ Features

- 🔍 Detects up to 10 object/scene labels per image
- 📊 Displays confidence scores (%) for each detected label
- 🟥 Draws bounding boxes around detected objects using Matplotlib
- ☁️ Fully cloud-integrated — images retrieved directly from S3 at runtime
- 🔐 IAM least-privilege policy — only the permissions this project needs, nothing more

---

## 🛠️ Prerequisites

- Python 3.8 or higher
- An AWS account (Free Tier eligible)
- AWS CLI installed and configured
- An S3 bucket with at least one image uploaded

---

## 📁 Project Structure

```
aws-rekognition-image-labeler/
│
├── app.py                  # Main Python script
├── requirements.txt        # Python dependencies
├── iam-policy.json         # Least-privilege IAM policy for this project
├── .gitignore              # Excludes sensitive files from version control
└── README.md               # You are here
```

---

## 🚀 Getting Started

### 1. Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/aws-rekognition-image-labeler.git
cd aws-rekognition-image-labeler
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Set Up AWS IAM

Create an IAM user with the least-privilege policy provided in `iam-policy.json`. This grants only the permissions required for this project:

- `s3:GetObject` — to retrieve images from the S3 bucket
- `rekognition:DetectLabels` — to run label detection

```bash
# Create the policy in your AWS account
aws iam create-policy \
  --policy-name RekognitionImageLabelerPolicy \
  --policy-document file://iam-policy.json
```

### 4. Configure AWS CLI

```bash
aws configure
```

Enter your IAM user's **Access Key ID**, **Secret Access Key**, region (`us-east-1`), and output format (`json`).

### 5. Upload an Image to S3

```bash
aws s3 cp your-image.jpg s3://your-bucket-name/
```

### 6. Run the Script

```bash
python app.py --photo your-image.jpg --bucket your-bucket-name
```

---

## 📦 Dependencies

```
boto3==1.34.0
matplotlib==3.8.0
Pillow==10.2.0
```

Install all at once:

```bash
pip install -r requirements.txt
```

---

## 🔐 IAM Least-Privilege Policy

This project follows the **principle of least privilege**. The `iam-policy.json` file grants only the minimum permissions required:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:GetObject"
      ],
      "Resource": "arn:aws:s3:::YOUR_BUCKET_NAME/*"
    },
    {
      "Effect": "Allow",
      "Action": [
        "rekognition:DetectLabels"
      ],
      "Resource": "*"
    }
  ]
}
```

> ⚠️ **Note:** The tutorial approach of attaching `AdministratorAccess` is intentionally avoided here. Always scope IAM permissions to the minimum required.

---

## 🧠 How It Works

1. The Python script initialises a **boto3 Rekognition client** in `us-east-1`
2. It calls `detect_labels()` with the S3 bucket name and image key
3. Rekognition returns up to 10 labels with:
   - Label name (e.g. "Person", "Shoe")
   - Confidence score (e.g. 99.91%)
   - Bounding box coordinates (normalised 0–1 values)
4. The image is retrieved from S3 via boto3 and loaded into memory using `BytesIO` (no disk write)
5. Matplotlib draws bounding boxes and confidence labels over the image

---

## 📊 Sample Output

```
Detected labels for Image_01.jpg
─────────────────────────────────
Label: Woman        | Confidence: 99.91%
Label: Person       | Confidence: 99.92%
Label: Shoe         | Confidence: 99.89%
Label: Shorts       | Confidence: 99.83%
...
Labels detected: 10
```

A pop-up window displays the original image with red bounding boxes and confidence labels rendered over each detected object.

---

## 💡 Key Learnings

- How to integrate **Amazon Rekognition** with **S3** using the boto3 SDK
- How to apply **IAM least-privilege** principles in a real project
- How to handle **binary image data** in memory using `BytesIO` without writing to disk
- How to normalise **bounding box coordinates** returned by Rekognition to pixel dimensions
- How to visualise AWS ML service output using **Matplotlib**

---

## 🔧 Potential Improvements

- [ ] Provision S3 bucket and IAM resources using **Terraform**
- [ ] Containerise the script using **Docker**
- [ ] Store detected labels in **DynamoDB** for persistence
- [ ] Expose results via **AWS Lambda + API Gateway**
- [ ] Add a **GitHub Actions** CI pipeline for automated testing

---

## 📜 License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

---

## 🙋 Author

**Chathura Dandeniya**  
AWS Solutions Architect Associate | CKA | Terraform Associate | AZ-104  
📍 Melbourne, VIC, Australia  
🔗 [LinkedIn](https://linkedin.com/in/YOUR_PROFILE) | [GitHub](https://github.com/YOUR_USERNAME)

---

> ⭐ If you found this project useful, consider giving it a star!
