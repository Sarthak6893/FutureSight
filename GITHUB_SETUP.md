# 🚀 GitHub Setup Guide for Future Sight

## Prerequisites

### 1. Install Git
Download and install Git from: https://git-scm.com/download/win

### 2. Create GitHub Account
Sign up at: https://github.com

## Step-by-Step GitHub Setup

### Step 1: Initialize Git Repository
```bash
# Navigate to your project directory
cd C:\Users\Sarthak\Capstone\future-sight

# Initialize git repository
git init

# Add all files to git
git add .

# Create initial commit
git commit -m "Initial commit: Future Sight AI Data Visualization"
```

### Step 2: Create GitHub Repository
1. Go to https://github.com
2. Click "New repository" (green button)
3. Repository name: `future-sight`
4. Description: `AI-powered data visualization platform`
5. Make it **Public** or **Private** (your choice)
6. **DO NOT** initialize with README (we already have one)
7. Click "Create repository"

### Step 3: Connect Local Repository to GitHub
```bash
# Add remote origin (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/future-sight.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Step 4: Verify Upload
1. Go to your GitHub repository
2. Check that all files are uploaded
3. Verify README.md displays correctly

## 🎯 Repository Structure

Your GitHub repository will contain:
```
future-sight/
├── .gitignore              # Git ignore rules
├── LICENSE                 # MIT License
├── README.md              # Project documentation
├── GITHUB_SETUP.md        # This setup guide
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

## 🔧 Important Notes

### Environment Variables
- **Never commit `.env` files** (they're in .gitignore)
- **Create `.env.example`** for other developers
- **Document required environment variables** in README

### Security
- **API keys are protected** by .gitignore
- **Virtual environments are ignored**
- **Node modules are ignored**

## 📋 Next Steps After Upload

### 1. Add Repository Description
- Go to your repository settings
- Add description: "AI-powered data visualization platform"
- Add topics: `ai`, `data-visualization`, `react`, `fastapi`, `python`

### 2. Enable GitHub Pages (Optional)
- Go to repository Settings → Pages
- Enable GitHub Pages for documentation

### 3. Add Badges (Optional)
Add to README.md:
```markdown
![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/future-sight)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/future-sight)
```

## 🚨 Troubleshooting

### If Git is not recognized:
1. Restart your terminal/command prompt
2. Check if Git is in your PATH
3. Reinstall Git if necessary

### If push fails:
```bash
# Check remote origin
git remote -v

# If wrong URL, fix it:
git remote set-url origin https://github.com/YOUR_USERNAME/future-sight.git
```

### If files are too large:
```bash
# Check file sizes
git ls-files | xargs ls -lh

# Add large files to .gitignore if needed
```

## 🎉 Success!

Once uploaded, your repository will be available at:
`https://github.com/YOUR_USERNAME/future-sight`

Share this link with others to showcase your AI data visualization project! 🔮✨

