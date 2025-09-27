import streamlit as st
import yt_dlp
import os
from pathlib import Path

class VideoDownloader:
    def __init__(self):
        self.supported_qualities = ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']
    
    def get_video_info(self, url):
        ydl_opts = {
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs', 'webpage']
                }
            },
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            }
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                # Get available formats
                formats = info.get('formats', [])
                available_qualities = ['best', 'worst']
                
                for fmt in formats:
                    if fmt.get('height'):
                        quality = f"{fmt['height']}p"
                        if quality not in available_qualities:
                            available_qualities.append(quality)
                
                # Sort qualities (best, worst, then by resolution descending)
                quality_order = ['best'] + sorted([q for q in available_qualities if q.endswith('p')], 
                                                key=lambda x: int(x[:-1]), reverse=True) + ['worst']
                available_qualities = [q for q in quality_order if q in available_qualities]
                
                return {
                    'title': info.get('title', 'Unknown'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'available_qualities': available_qualities,
                    'thumbnail': info.get('thumbnail', None),
                    'formats': formats
                }
        except Exception as e:
            return None
    
    def download_video(self, url, download_path, quality='best', audio_only=False):
        # Progress tracking
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Stop flag
        if 'stop_download' not in st.session_state:
            st.session_state.stop_download = False
        
        def progress_hook(d):
            if st.session_state.stop_download:
                raise Exception("Download cancelled by user")
                
            if d['status'] == 'downloading':
                speed = d.get('speed', 0)
                speed_str = f"{speed/1024/1024:.1f} MB/s" if speed else "Unknown"
                
                if 'total_bytes' in d:
                    percent = d['downloaded_bytes'] / d['total_bytes']
                    progress_bar.progress(percent)
                    status_text.markdown(f"📥 **Downloading... {percent:.1%}** - Speed: {speed_str}")
                elif 'total_bytes_estimate' in d:
                    percent = d['downloaded_bytes'] / d['total_bytes_estimate']
                    progress_bar.progress(min(percent, 1.0))
                    status_text.markdown(f"📥 **Downloading... {percent:.1%}** - Speed: {speed_str}")
            elif d['status'] == 'finished':
                progress_bar.progress(1.0)
                status_text.markdown("✅ **Download completed!**")
        
        ydl_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,
            'progress_hooks': [progress_hook],
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'referer': 'https://www.youtube.com/',
            'extractor_args': {
                'youtube': {
                    'skip': ['dash', 'hls'],
                    'player_skip': ['configs', 'webpage']
                }
            },
            'http_headers': {
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate'
            }
        }
        
        if audio_only:
            ydl_opts['format'] = 'bestaudio/best'
        else:
            if quality == 'best':
                ydl_opts['format'] = 'best[ext=mp4]/best'
            elif quality == 'worst':
                ydl_opts['format'] = 'worst'
            elif quality in ['2160p', '1440p', '1080p', '720p', '480p', '360p', '240p', '144p']:
                height = quality[:-1]
                ydl_opts['format'] = f'best[height<={height}][ext=mp4]/best[height<={height}]/best'
        
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            return True
        except Exception as e:
            if "cancelled by user" in str(e):
                return False
            st.error(f"Download failed: {str(e)}")
            return False



def main():
    st.set_page_config(page_title="YouTube Video Downloader", page_icon="📹")
    
    # Custom CSS styling
    st.markdown("""
    <style>
    .video-card {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        margin: 15px 0;
        border: 1px solid #e0e0e0;
    }
    .download-section {
        background: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 15px 0;
        border: 1px solid #e0e0e0;
    }
    .stButton > button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton > button:hover {
        transform: translateY(-1px);
    }
    .stProgress > div > div > div {
        background: linear-gradient(45deg, #4CAF50, #45a049);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.title("📹 YouTube Video Downloader")
    st.write("Download videos from YouTube and other platforms")
    
    downloader = VideoDownloader()
    
    # Theme toggle in sidebar
    with st.sidebar:
        st.header("🎨 Settings")
        theme = st.selectbox("Theme", ["Light", "Dark"])
        
        if theme == "Dark":
            st.markdown("""
            <style>
            .stApp {
                background-color: #1e1e1e;
                color: white;
            }
            .video-card {
                background: #2d2d2d;
                color: white;
                border: 1px solid #444;
            }
            .download-section {
                background: #2d2d2d;
                color: white;
                border: 1px solid #444;
            }
            </style>
            """, unsafe_allow_html=True)
    
    # Initialize session state
    if 'video_info' not in st.session_state:
        st.session_state.video_info = None
    if 'current_url' not in st.session_state:
        st.session_state.current_url = ""
    
    # URL input
    url = st.text_input("Enter video URL:", placeholder="https://youtu.be/...")
    
    # Search button
    search_clicked = st.button("🔍 Search Video")
    
    if not url and search_clicked:
        st.warning("Please enter a URL")
    
    if search_clicked and url:
        # Get video info
        with st.spinner("Getting video information..."):
            st.session_state.video_info = downloader.get_video_info(url)
            st.session_state.current_url = url
    
    # Display video info if available
    if st.session_state.video_info:
        info = st.session_state.video_info
        st.success("✅ Valid URL")
        
        # Video info card
        st.markdown('<div class="video-card">', unsafe_allow_html=True)
        
        # Show thumbnail if available
        if info.get('thumbnail'):
            col1, col2 = st.columns([1, 2])
            with col1:
                st.image(info['thumbnail'], width=200, caption="Video Thumbnail")
            with col2:
                st.write(f"**📺 Title:** {info['title']}")
                st.write(f"**👤 Uploader:** {info['uploader']}")
                duration = f"{info['duration']//60}:{info['duration']%60:02d}" if info['duration'] else "Unknown"
                st.write(f"**⏱️ Duration:** {duration}")
        else:
            st.write(f"**📺 Title:** {info['title']}")
            st.write(f"**👤 Uploader:** {info['uploader']}")
            duration = f"{info['duration']//60}:{info['duration']%60:02d}" if info['duration'] else "Unknown"
            st.write(f"**⏱️ Duration:** {duration}")
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Download options section
        st.markdown('<div class="download-section">', unsafe_allow_html=True)
        st.subheader("📥 Download Options")
        
        # Quality cards
        st.write("**Select Quality:**")
        if 'selected_quality' not in st.session_state:
            st.session_state.selected_quality = info['available_qualities'][0]
        
        cols = st.columns(min(len(info['available_qualities']), 4))
        for i, qual in enumerate(info['available_qualities']):
            with cols[i % 4]:
                if st.button(f"📺 {qual}", key=f"qual_{i}", 
                           type="primary" if st.session_state.selected_quality == qual else "secondary"):
                    st.session_state.selected_quality = qual
        
        quality = st.session_state.selected_quality
        audio_only = st.checkbox("🎵 Audio only")
        
        # File size estimation
        def estimate_file_size(formats, quality):
            if quality == 'best' or quality == 'worst':
                return "Unknown"
            try:
                height = int(quality[:-1])
                for fmt in formats:
                    if fmt.get('height') == height and fmt.get('filesize'):
                        size_mb = fmt['filesize'] / (1024 * 1024)
                        return f"{size_mb:.1f} MB"
                    elif fmt.get('height') == height and fmt.get('filesize_approx'):
                        size_mb = fmt['filesize_approx'] / (1024 * 1024)
                        return f"~{size_mb:.1f} MB"
                return "Unknown"
            except:
                return "Unknown"
        
        estimated_size = estimate_file_size(info.get('formats', []), quality)
        st.info(f"💾 Estimated file size: {estimated_size}")
            
        # Download path
        download_path = str(Path.home() / "Downloads")
        st.info(f"💻 Files will be saved to: {download_path}")
        st.markdown('</div>', unsafe_allow_html=True)
            
        # Download button
        col1, col2 = st.columns([3, 1])
        with col1:
            download_clicked = st.button("📥 Download", type="primary")
        
        if download_clicked:
            os.makedirs(download_path, exist_ok=True)
            st.session_state.stop_download = False
            
            # Show active stop button during download
            with col2:
                if st.button("❌ Stop", key="stop_active"):
                    st.session_state.stop_download = True
                    st.warning("Download cancelled!")
            
            success = downloader.download_video(st.session_state.current_url, download_path, quality, audio_only)
            
            if success and not st.session_state.stop_download:
                st.success("✅ Download completed!")
                st.info(f"💻 File saved to: {download_path}")
            elif st.session_state.stop_download:
                st.warning("❌ Download cancelled by user")
    
    elif search_clicked:
        st.error("❌ Invalid URL or unable to extract video information")

if __name__ == "__main__":
    main()
