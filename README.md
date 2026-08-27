# Chronicle ✍️

> **A personal story-writing platform built to capture, organize, and relive your thoughts.**

Chronicle is a full-stack personal writing application designed for people who want a focused space to write, organize, and reflect on their stories.

It combines a distraction-free writing editor with a searchable story library, writing analytics, streak tracking, writing goals, prompts, ambient soundscapes, and data portability.

## ✨ Features

### 📝 Writing Editor

* Create and edit personal stories
* Rich-text formatting with bold, italic, underline, headings, lists, quotes, and links
* Add tags to organize stories
* Automatic word-count calculation
* Estimated reading time
* Save and continue editing existing stories
* Dedicated immersive **Read Mode**

### 📚 Story Library

* Browse all saved stories in a timeline
* Search stories by title, content, or tags
* Filter stories by tags
* Quickly open stories for editing
* Organize your writing chronologically

### 📊 Writing Analytics

* Total stories written
* Total words written
* Average words per story
* Current writing streak
* Longest writing streak
* Most active writing day
* Completed writing goals
* Tag/category usage breakdown
* GitHub-style **365-day writing heatmap**

### 🎯 Writing Goals

Set personal writing goals based on:

* Word count
* Writing time

Chronicle tracks your progress and records completed goals.

### 💡 Writing Prompts

Need inspiration?

Chronicle includes a prompt system that lets you select a genre, generate a writing prompt, and immediately use it inside the editor.

### 🎧 Ambient Soundscapes

Create a more immersive writing environment with built-in soundscapes and individual volume controls.

### 🌗 Theme Support

* Dark theme
* Light theme
* Theme preference saved locally

### 💾 Data Portability

Your writing should remain yours.

Chronicle supports:

* Exporting your stories as JSON
* Importing a previous JSON backup
* Restoring your entire story collection from a backup file

### 📱 Responsive Interface

The interface is designed to work across desktop and mobile layouts, including a mobile navigation drawer and responsive writing workspace.

### 🌐 Local Network Access

The Express server also detects the machine's local IPv4 addresses so Chronicle can be accessed from other devices connected to the same Wi-Fi network.

---

## 🛠️ Tech Stack

### Frontend

* HTML5
* CSS3
* Vanilla JavaScript
* ES Modules
* SVG
* Google Fonts

### Backend

* Node.js
* Express.js
* CORS

### Storage

* JSON-based local database (`server/db.json`)

### Architecture

```text
Chronicle
├── public/
│   ├── index.html
│   ├── index.css
│   └── js/
│       ├── api.js
│       ├── app.js
│       ├── dashboard.js
│       ├── editor.js
│       ├── library.js
│       ├── particles.js
│       └── soundscapes.js
│
├── server/
│   ├── db.json
│   └── server.js
│
├── package.json
└── package-lock.json
```

---

## 🚀 Getting Started

### Prerequisites

Make sure you have:

* [Node.js](https://nodejs.org/) installed
* npm installed

### 1. Clone the repository

```bash
git clone https://github.com/Kanduriavinash/chronicle.git
cd chronicle
```

### 2. Install dependencies

```bash
npm install
```

### 3. Start the server

```bash
npm start
```

The application will start on:

```text
http://localhost:3000
```

Open the URL in your browser.

---

## 📡 Access Chronicle From Another Device

When the server starts, Chronicle checks for available local network IPv4 addresses.

If your computer and phone are connected to the same Wi-Fi network, use the displayed address:

```text
http://YOUR_LOCAL_IP:3000
```

For example:

```text
http://192.168.1.10:3000
```

This makes it possible to use Chronicle from another device on the same local network.

---

## 🔌 API

Chronicle uses a lightweight REST API for story management.

| Method   | Endpoint             | Description           |
| -------- | -------------------- | --------------------- |
| `GET`    | `/api/stories`       | Get all stories       |
| `GET`    | `/api/stories/:id`   | Get a single story    |
| `POST`   | `/api/stories`       | Create a story        |
| `PUT`    | `/api/stories/:id`   | Update a story        |
| `DELETE` | `/api/stories/:id`   | Delete a story        |
| `POST`   | `/api/backup/import` | Import a story backup |

The backend stores story data in:

```text
server/db.json
```

---

## 🧠 How It Works

Chronicle follows a simple client-server architecture.

```text
Browser
   │
   ▼
Frontend UI
   │
   ├── Library
   ├── Editor
   ├── Dashboard
   ├── Prompts
   ├── Goals
   └── Soundscapes
   │
   ▼
REST API
   │
   ▼
Express.js Server
   │
   ▼
server/db.json
```

The frontend communicates with the Express backend through REST endpoints, while the server persists stories in a JSON file.

---

## 📈 Analytics & Heatmap

The dashboard calculates writing activity from your saved stories.

The heatmap represents daily writing volume across roughly the previous year:

```text
Less Writing  ░ ▒ ▓ █  More Writing
```

Statistics are calculated dynamically from story metadata such as word count, dates, tags, and completed goals.

---

## 🔐 Data & Privacy

Chronicle is designed as a local-first personal writing application.

Your stories are stored in the application's local JSON database:

```text
server/db.json
```

No external database is required to run the project.

For additional safety, use the built-in JSON backup/export feature to keep copies of your writing.

> **Note:** Because the application uses a JSON file as its database, it is best suited for personal/local use rather than large-scale multi-user deployments.

---

## 🎨 Design Philosophy

Chronicle is built around the idea that writing should feel calm, personal, and immersive.

The UI uses:

* A minimal writing-focused layout
* Dark/light themes
* Serif typography for reading and writing
* Responsive navigation
* Ambient visual effects
* Interactive statistics
* Focused editing and reading experiences

---

## 🔮 Future Improvements

Potential improvements include:

* Cloud synchronization
* User authentication
* PostgreSQL or MongoDB storage
* Multi-user accounts
* Richer analytics
* Markdown import/export
* PDF/HTML story export
* AI-powered writing assistance
* Version history
* Automatic cloud backups
* Cross-device synchronization
* PWA/offline support

---

## 🤝 Contributing

Contributions and suggestions are welcome.

### Fork the repository

```bash
git fork https://github.com/Kanduriavinash/chronicle
```

### Create a feature branch

```bash
git checkout -b feature/your-feature
```

### Commit your changes

```bash
git add .
git commit -m "Add your feature"
```

### Push the branch

```bash
git push origin feature/your-feature
```

Then open a Pull Request.

---

## 📄 License

This project does not currently specify a license.

---

## 👨‍💻 Author

**Kanduriavinash**

Built with ❤️ as a personal space for writing, reflection, and storytelling.

### ⭐ Support the Project

If you find Chronicle useful, consider giving the repository a ⭐ on GitHub.

[View Chronicle on GitHub](https://github.com/Kanduriavinash/chronicle)
