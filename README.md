# AI-Generated Image Detection

A multimodal pipeline for detecting **AI-generated images** from Instagram-style data by combining visual information with **EXIF metadata** and **social-media metadata**.

The project starts from a pre-trained image classifier and progressively adapts it to the target domain through fine-tuning and semi-supervised learning. It then extends the image-only model with metadata-based branches and finally combines visual, EXIF and textual/social features in a single model.

## Project overview

The main stages of the project are:

1. **Baseline evaluation** of an out-of-the-box AI-vs-human image detector.
2. **CNN fine-tuning** on the labeled dataset.
3. **Semi-supervised learning** with confidence-based pseudo-labeling of unlabeled images.
4. **CNN + EXIF metadata** model.
5. **CNN + social-media metadata** model, including caption embeddings from multilingual BERT.
6. **Final multimodal model** combining image features, EXIF metadata, numerical social metadata and text embeddings.

The goal is not only to classify images based on visual artifacts, but also to study whether auxiliary information associated with an image can improve detection performance.

## Methodology

### Image model

The visual backbone is initialized from the Hugging Face model:

`Ateeqq/ai-vs-human-image-detector`

The project uses the corresponding `AutoImageProcessor` and `AutoModelForImageClassification` from the Transformers library.

### Semi-supervised learning

The labeled data is split into training, validation and test subsets. The CNN is first fine-tuned using the labeled training set and weighted cross-entropy loss.

Unlabeled images are then classified by the current model. Predictions with confidence above **0.98** are accepted as pseudo-labels and included in the following training iteration with a lower sample weight than manually labeled examples.

The implemented SSL configuration uses:

- 3 pseudo-labeling iterations
- batch size: 16
- learning rate: `5e-6`
- weight decay: `1e-4`
- 5 fine-tuning epochs per iteration
- labeled sample weight: `1.0`
- pseudo-labeled sample weight: `0.3`
- higher loss weight for the AI class to account for class imbalance
- early stopping based on validation loss

By the final SSL iteration, **1,047 pseudo-labeled images** are added to the original labeled training data.

### EXIF metadata

EXIF and image-file metadata are extracted and processed separately from the visual input. The metadata pipeline includes information such as:

- image dimensions and format
- ICC/color-profile information
- camera make and model
- lens and exposure information when available
- editing software
- orientation and JPEG-related information
- GPS fields when present
- file timestamps and other forensic metadata

Numerical metadata is normalized and categorical metadata is encoded before being concatenated with the visual feature representation.

### Social-media metadata

The social branch uses available post-level information such as numerical social features and associated caption text.

Text is processed with **`bert-base-multilingual-cased`**. BERT parameters are frozen and its contextual text representation is projected before being combined with the CNN features and numerical metadata.

### Final multimodal model

The final architecture combines:

```text
Image
  ↓
Pre-trained vision backbone
  ↓
Visual features ──────────────┐
                              │
EXIF metadata → preprocessing ├──→ Feature fusion → Binary classifier
                              │
Social numerical metadata ───┤
                              │
Caption → multilingual BERT ──┘
```

The CNN and BERT backbones are used as feature extractors, while additional projection and classification layers learn how to combine the different modalities.

## Results

Performance reported by the project notebooks on the held-out test set:

| Model | Accuracy | Precision (AI) | Recall (AI) | F1 (AI) |
| --- | ---: | ---: | ---: | ---: |
| Out-of-the-box image detector | 0.5000 | 0.4390 | 0.9000 | 0.5902 |
| Fine-tuned CNN + SSL | 0.8600 | 0.9333 | 0.7000 | 0.8000 |
| CNN + EXIF metadata | 0.8600 | 0.7600 | 0.9500 | 0.8444 |
| CNN + social-media metadata | 0.7959 | 0.7083 | 0.8500 | 0.7727 |
| **CNN + EXIF + social metadata** | **0.8776** | **0.7692** | **1.0000** | **0.8696** |

The final multimodal model achieves the highest accuracy and F1 score in the experiments and detects all AI-generated examples in its test subset, corresponding to an AI-class recall of **1.00**.

## Repository structure

```text
ai-detection-project/
├── Code/
│   ├── main.ipynb
│   ├── Test CNN.ipynb
│   └── meta.py
├── trained_models/
│   └── .gitkeep
├── Group_14_Project_Final_Report-2.pdf
├── README.md
├── LICENSE
└── .gitignore
```

### Files

- **`Code/main.ipynb`** — main experimental pipeline: CNN fine-tuning, semi-supervised learning, pseudo-labeling, metadata integration and multimodal models.
- **`Code/Test CNN.ipynb`** — evaluation of the original pre-trained CNN on the project test set before domain-specific fine-tuning.
- **`Code/meta.py`** — EXIF/file-metadata extraction using ExifTool and creation of the metadata CSV.
- **`Group_14_Project_Final_Report-2.pdf`** — complete project report.
- **`trained_models/`** — placeholder for trained model checkpoints; the full checkpoints are stored externally because of their size.

## Dataset and trained models

The full dataset and trained model checkpoints are not stored directly in this repository because of their size.

They are available here:

**[Google Drive — Dataset & Trained Models](https://drive.google.com/drive/folders/1EmGZUGHQHH5jInV2-H-yIqll96aic3nE?usp=drive_link)**

The notebooks were developed around a Google Drive / Google Colab workflow, so local paths may need to be adapted if the project is executed outside Colab.

## Running the project

The main notebook is designed to run in **Google Colab**.

### 1. Clone the repository

```bash
git clone https://github.com/paolapinna03/ai-detection-project.git
cd ai-detection-project
```

### 2. Download the data

Download the dataset and trained models from the Google Drive link above.

The notebook expects separate directories for:

```text
Images/
├── Labeled/
├── Unlabeled/
└── Test/
```

with labeled/test images organized into `AI` and `Not_AI` classes.

### 3. Install the main dependencies

```bash
pip install torch torchvision transformers scikit-learn pandas numpy pillow
```

Metadata extraction additionally requires **ExifTool**.

### 4. Open the notebook

Run:

`Code/main.ipynb`

and update `ROOT` if your Drive or local directory structure differs from the original project setup.

## Main technologies

- Python
- PyTorch
- Hugging Face Transformers
- CNN / Vision Transformer-based image classification
- Semi-supervised learning and pseudo-labeling
- BERT
- pandas / NumPy
- scikit-learn
- EXIF / forensic image metadata
- Google Colab

## Project report

A detailed description of the methodology, experiments and analysis is available in [`Group_14_Project_Final_Report-2.pdf`](./Group_14_Project_Final_Report-2.pdf).

## License

See [`LICENSE`](./LICENSE).
