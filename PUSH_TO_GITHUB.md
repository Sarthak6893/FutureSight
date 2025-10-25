# 🚀 Push Future Sight to GitHub Repository

## Your Repository URL
**https://github.com/Sarthak6893/FutureSight**

## Step 1: Install Git

### Download and Install Git
1. **Go to:** https://git-scm.com/download/win
2. **Download** the latest version for Windows
3. **Run the installer** with default settings
4. **Restart** your command prompt/terminal after installation

### Verify Installation
```bash
git --version
```
You should see something like: `git version 2.x.x`

## Step 2: Configure Git (First Time Only)

```bash
# Set your name and email (replace with your details)
git config --global user.name "Sarthak6893"
git config --global user.email "your-email@example.com"
```

## Step 3: Push Project to GitHub

### Navigate to Project Directory
```bash
cd C:\Users\Sarthak\Capstone\future-sight
```

### Initialize Git Repository
```bash
git init
```

### Add All Files
```bash
git add .
```

### Create Initial Commit
```bash
git commit -m "Initial commit: Future Sight AI Data Visualization Platform"
```

### Connect to Your GitHub Repository
```bash
git remote add origin https://github.com/Sarthak6893/FutureSight.git
```

### Push to GitHub
```bash
git branch -M main
git push -u origin main
```

## Step 4: Verify Upload

1. **Go to:** https://github.com/Sarthak6893/FutureSight
2. **Check that all files are uploaded**
3. **Verify README.md displays correctly**

## 🎯 What Will Be Uploaded

Your repository will contain:
```
FutureSight/
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md              # Project documentation
├── GITHUB_SETUP.md        # Setup guide
├── PUSH_TO_GITHUB.md      # This guide
├── setup_github.bat       # Automated setup
├── backend/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env
│   └── venv/ (ignored)
├── frontend/
│   ├── src/
│   ├── package.json
│   └── node_modules/ (ignored)
└── sample_data.csv
```

## 🔧 Troubleshooting

### If Git is not recognized after installation:
1. **Restart your computer**
2. **Or restart your command prompt**
3. **Check if Git is in your PATH**

### If push fails with authentication:
```bash
# Use GitHub CLI or Personal Access Token
git remote set-url origin https://github.com/Sarthak6893/FutureSight.git
```

### If files are too large:
- Check `.gitignore` file
- Large files should be excluded automatically

## 🎉 Success!

Once uploaded, your repository will be available at:
**https://github.com/Sarthak6893/FutureSight**

## 📋 Quick Commands Summary

```bash
# After installing Git, run these commands:
cd C:\Users\Sarthak\Capstone\future-sight
git init
git add .
git commit -m "Initial commit: Future Sight AI Data Visualization Platform"
git remote add origin https://github.com/Sarthak6893/FutureSight.git
git branch -M main
git push -u origin main
```

## 🚨 Important Notes

- **API keys are protected** by .gitignore
- **Virtual environments are ignored**
- **Node modules are ignored**
- **Only source code is uploaded**

Your Future Sight project will be live on GitHub! 🔮✨
