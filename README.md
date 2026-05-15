# GitHub Profile Updater

**GitHub Profile Updater** is a Python automation tool designed to create a dynamic, professional GitHub profile README (`username/username`) by aggregating information from your private repositories.

It fetches selected repositories via the GitHub API, extracts key metadata (tech stack, details, README content), and generates a polished profile page featuring a **"Project Highlights"** table and collapsible **"Project Details"** sections.

## ✨ Key Features

-   **Private Repo Aggregation**: Securely fetches data from specified private repositories using a Personal Access Token (PAT).
-   **Dynamic Tech Stack Badges**: Automatically generates shields.io badges for languages and frameworks used in each project.
-   **Manual Enrichment**: Allows manual mapping of specific technologies (e.g., Spring Boot, AWS, Oracle) to projects for a richer portfolio.
-   **Smart Content Cleaning**: Sanitize fetched README content by removing H1 tags and masking private images, while preserving public badges.
-   **Automated Updates**: Generates the markdown and directly pushes the update to your GitHub profile repository.
-   **Custom sorting**: Organize your projects in a specific order to tell your story best.

## 🛠️ Prerequisites

-   Python 3.8+
-   A GitHub Personal Access Token (PAT) with `repo` scope.

## 🚀 Getting Started

### 1. Clone the repository
```bash
git clone https://github.com/bulls1223/github-profile-updater.git
cd github-profile-updater
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure Environment
Create a `.env` file in the root directory (you can copy `.env.example`):
```bash
GITHUB_PAT=your_github_personal_access_token
TARGET_REPO=your_username/your_username
```

### 4. Run the Script
```bash
python main.py
```
This will:
1.  Fetch your repositories.
2.  Generate a `GENERATED_PROFILE.md` file locally.
3.  Push the updated content to your target GitHub profile repository.

## ⚙️ Configuration

You can customize the script by modifying `main.py`:
-   **`TECH_CONFIG`**: Add or modify badge colors and logos for different technologies.
-   **`EXTRA_REPO_TECH`**: Manually assign technologies to specific repositories.
-   **`project_order`**: Define the display order of your projects.

## 📝 License

This project is open source and available under the [MIT License](LICENSE).


<!-- YOLO Achievement Test -->

<!-- Pair Extraordinaire Achievement Test -->

<!-- Silver Shark Achievement Contribution #1 -->

<!-- Silver Shark Achievement Contribution #2 -->

<!-- Silver Shark Achievement Contribution #3 -->

<!-- Silver Shark Achievement Contribution #4 -->

<!-- Silver Shark Achievement Contribution #5 -->

<!-- Silver Shark Achievement Contribution #6 -->

<!-- Silver Shark Achievement Contribution #7 -->

<!-- Silver Shark Achievement Contribution #8 -->

<!-- Silver Shark Achievement Contribution #9 -->

<!-- Silver Shark Achievement Contribution #10 -->

<!-- Silver Shark Achievement Contribution #11 -->

<!-- Final Silver Shark Contribution #15 -->

<!-- Final Silver Shark Contribution #16 -->