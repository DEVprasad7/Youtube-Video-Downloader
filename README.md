# 📹 YouTube Video Downloader

A modern, web-based YouTube video downloader built with Streamlit and yt-dlp. Features a clean UI with dark/light themes, real-time progress tracking, and quality selection.

## 🚀 Features

- **Multi-Platform Support**: Download from YouTube and other video platforms
- **Quality Selection**: Choose from available video qualities (720p, 1080p, etc.)
- **Audio-Only Downloads**: Extract audio tracks only
- **Real-Time Progress**: Live download progress with speed indicators
- **Modern UI**: Clean interface with dark/light theme toggle
- **Video Thumbnails**: Preview video thumbnails before download
- **File Size Estimation**: See estimated download size
- **Download Control**: Start/stop downloads mid-process

## 🛠️ Installation

### Requirements
```bash
pip install streamlit yt-dlp
```

### Local Setup
1. Clone or download the project
2. Install dependencies: `pip install -r requirements.txt`
3. Run the app: `streamlit run main.py`

### Deployment
Deploy on [Streamlit Community Cloud](https://share.streamlit.io) by connecting your GitHub repository.

## 📁 Project Structure

```
├── main.py           # Main application file
├── requirements.txt  # Python dependencies
└── README.md        # This file
```

## 🔧 Code Architecture

### Core Components

#### 1. VideoDownloader Class
The main class handling all video operations:

```python
class VideoDownloader:
    def __init__(self):
        self.supported_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
```

**Methods:**

- `get_video_info(url)`: Extracts video metadata without downloading
- `download_video(url, path, quality, audio_only)`: Downloads video with progress tracking

#### 2. Video Information Extraction

```python
def get_video_info(self, url):
    ydl_opts = {
        'quiet': True,
        'user_agent': 'Mozilla/5.0...',  # Bypass YouTube restrictions
        'extractor_args': {'youtube': {'skip': ['dash', 'hls']}}  # Skip problematic formats
    }
```

**Extracted Data:**
- Video title, uploader, duration
- Available quality formats
- Video thumbnail URL
- Format details for size estimation

#### 3. Download Engine

```python
def download_video(self, url, download_path, quality='best', audio_only=False):
    # Progress tracking setup
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def progress_hook(d):
        # Real-time progress updates
        if d['status'] == 'downloading':
            percent = d['downloaded_bytes'] / d['total_bytes']
            progress_bar.progress(percent)
```

**Key Features:**
- Real-time progress bar updates
- Download speed calculation
- User cancellation support
- Error handling and recovery

#### 4. yt-dlp Configuration

```python
ydl_opts = {
    'outtmpl': '%(title)s.%(ext)s',           # File naming pattern
    'noplaylist': True,                        # Single video only
    'progress_hooks': [progress_hook],         # Progress callback
    'user_agent': 'Mozilla/5.0...',          # Browser simulation
    'extractor_args': {'youtube': {'skip': ['dash', 'hls']}},  # Format filtering
    'format_sort': ['res:720', 'ext:mp4:m4a'] # Quality preference
}
```

### UI Components

#### 1. Custom CSS Styling

```css
.video-card {
    background: white;
    border-radius: 10px;
    padding: 20px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}
```

**Styling Features:**
- Card-based layout for video info
- Rounded corners and shadows
- Hover effects on buttons
- Animated progress bars

#### 2. Theme System

```python
theme = st.selectbox("Theme", ["Light", "Dark"])
if theme == "Dark":
    # Apply dark theme CSS
```

**Theme Options:**
- Light: White backgrounds, dark text
- Dark: Dark backgrounds, light text
- Dynamic CSS injection

#### 3. Quality Selection Interface

```python
cols = st.columns(min(len(info['available_qualities']), 4))
for i, qual in enumerate(info['available_qualities']):
    with cols[i % 4]:
        if st.button(f"📺 {qual}", key=f"qual_{i}"):
            st.session_state.selected_quality = qual
```

**Features:**
- Visual quality cards instead of dropdown
- Dynamic button highlighting
- Session state management

#### 4. File Size Estimation

```python
def estimate_file_size(formats, quality):
    height = int(quality[:-1])
    for fmt in formats:
        if fmt.get('height') == height and fmt.get('filesize'):
            size_mb = fmt['filesize'] / (1024 * 1024)
            return f"{size_mb:.1f} MB"
```

### Session State Management

```python
if 'video_info' not in st.session_state:
    st.session_state.video_info = None
if 'current_url' not in st.session_state:
    st.session_state.current_url = ""
if 'selected_quality' not in st.session_state:
    st.session_state.selected_quality = info['available_qualities'][0]
```

**Managed States:**
- `video_info`: Cached video metadata
- `current_url`: Active video URL
- `selected_quality`: User's quality choice
- `stop_download`: Download cancellation flag

### Error Handling

#### 1. YouTube 403 Forbidden Fix
```python
'user_agent': 'Mozilla/5.0...',  # Simulate real browser
'extractor_args': {'youtube': {'skip': ['dash', 'hls']}}  # Skip problematic formats
```

#### 2. Download Cancellation
```python
if st.session_state.stop_download:
    raise Exception("Download cancelled by user")
```

#### 3. Format Fallbacks
```python
if quality == 'best':
    ydl_opts['format'] = 'best[ext=mp4]/best'
elif quality == 'worst':
    ydl_opts['format'] = 'worst'
else:
    height = quality[:-1]
    ydl_opts['format'] = f'best[height<={height}][ext=mp4]/best[height<={height}]/best'
```

## 🎯 User Flow

1. **URL Input**: User enters YouTube URL
2. **Search**: Click "🔍 Search Video" to fetch metadata
3. **Preview**: View thumbnail, title, duration, uploader
4. **Quality Selection**: Choose from available quality cards
5. **Options**: Toggle audio-only mode if needed
6. **Download**: Click "📥 Download" to start
7. **Progress**: Monitor real-time progress and speed
8. **Completion**: File saved to Downloads folder

## 🔧 Configuration Options

### Download Formats
- **Video**: MP4 preferred, fallback to best available
- **Audio**: Best audio quality available
- **Quality**: User-selectable from available options

### File Naming
```python
'outtmpl': '%(title)s.%(ext)s'  # Uses video title as filename
```

### Download Location
```python
download_path = str(Path.home() / "Downloads")  # User's Downloads folder
```

## 🚨 Troubleshooting

### Common Issues

1. **403 Forbidden Error**
   - Fixed with user agent and format skipping
   - Bypasses YouTube's anti-bot measures

2. **No Formats Available**
   - Some videos may be region-restricted
   - Try different quality options

3. **Download Fails**
   - Check internet connection
   - Verify URL is valid and accessible

### Debug Mode
Set `'quiet': False` in ydl_opts for verbose logging.

## 📝 Dependencies

- **streamlit**: Web app framework
- **yt-dlp**: Video download engine
- **pathlib**: File path handling
- **os**: Operating system interface

## 🔒 Security Features

- No file system access beyond Downloads folder
- User agent spoofing for privacy
- No credential storage or user data collection
- Client-side processing only

## 🌐 Browser Compatibility

- Chrome/Chromium (recommended)
- Firefox
- Safari
- Edge

## 📱 Device Support

- **Desktop**: Full functionality
- **Mobile**: View-only (downloads not supported in web browsers)

## 🔄 Updates

The app automatically uses the latest yt-dlp version for maximum compatibility with video platforms.

## 📄 License

This project is for educational purposes. Respect video platform terms of service and copyright laws.