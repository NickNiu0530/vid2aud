import os
import subprocess
import argparse
import sys

def check_ffmpeg():
    """检查ffmpeg是否已安装"""
    try:
        subprocess.run(["which", "ffmpeg"], check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def install_dependencies():
    """安装必要的依赖库"""
    print("\n" + "=" * 60)
    print("正在检查并安装依赖库...")
    print("=" * 60)
    
    # 检查ffmpeg
    if not check_ffmpeg():
        print("\n警告: ffmpeg 未安装")
        print("ffmpeg 是提取和转换音频所必需的工具")
        print("请按照以下命令安装ffmpeg:")
        print("  • macOS: brew install ffmpeg")
        print("  • Linux: sudo apt-get install ffmpeg")
        print("  • Windows: choco install ffmpeg")
        print("\n继续执行，但音频格式转换可能会失败...")
    else:
        print("ffmpeg 已安装")
    
    # 检查yt-dlp
    try:
        subprocess.run(["pip3", "show", "yt-dlp"], check=True, capture_output=True)
        print("yt-dlp 已安装")
    except subprocess.CalledProcessError:
        print("正在安装 yt-dlp...")
        try:
            subprocess.run(["pip3", "install", "yt-dlp"], check=True, capture_output=True)
            print("yt-dlp 安装成功")
        except Exception as e:
            print(f"安装 yt-dlp 失败: {e}")
            return False
    
    return True

def extract_audio(video_url, output_dir="audio", audio_format="mp3", quality="128k"):
    """
    从视频中提取音频
    
    Args:
        video_url: 视频的URL
        output_dir: 输出音频文件的目录
        audio_format: 音频格式，默认为mp3
        quality: 音频质量，默认为128k
    
    Returns:
        bool: 提取是否成功
    """
    print(f"\n" + "=" * 60)
    print(f"开始从视频提取音频")
    print(f"视频URL: {video_url}")
    print(f"输出目录: {output_dir}")
    print(f"音频格式: {audio_format}")
    print(f"音频质量: {quality}")
    print("=" * 60)
    
    # 创建输出目录
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"创建输出目录: {output_dir}")
        except Exception as e:
            print(f"创建输出目录失败: {e}")
            return False
    
    # 尝试使用Python模块方式运行yt-dlp
    try:
        import yt_dlp
        
        # 配置选项
        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': audio_format,
                'preferredquality': quality,
            }],
            'outtmpl': f'{output_dir}/%(title)s.%(ext)s',
            'quiet': False,
            'no_warnings': False,
        }
        
        print(f"\n使用yt-dlp模块提取音频")
        
        # 执行下载和提取
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            title = info.get('title', '未知')
            print(f"\n" + "=" * 60)
            print(f"提取音频成功!")
            print(f"视频标题: {title}")
            print(f"输出目录: {output_dir}")
            print("=" * 60)
            return True
    except ImportError:
        print("\nyt-dlp模块导入失败，尝试使用命令行方式...")
        # 构建yt-dlp命令（作为备选方案）
        cmd = [
            "python3", "-m", "yt_dlp",  # 使用Python模块方式运行
            "-x",  # 仅提取音频
            "--audio-format", audio_format,  # 设置音频格式
            "--audio-quality", quality,  # 设置音频质量
            "-o", f"{output_dir}/%(title)s.%(ext)s",  # 输出文件名格式
            video_url  # 视频URL
        ]
        
        print(f"执行命令: {' '.join(cmd)}")
        
        try:
            # 执行命令
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            print("\n" + "=" * 60)
            print("提取音频成功!")
            print(f"输出: {result.stdout}")
            print("=" * 60)
            return True
        except subprocess.CalledProcessError as e:
            print("\n" + "=" * 60)
            print(f"提取音频失败: {e}")
            print(f"错误输出: {e.stderr}")
            print("=" * 60)
            return False
        except Exception as e:
            print("\n" + "=" * 60)
            print(f"发生未知错误: {e}")
            print("=" * 60)
            return False
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"发生未知错误: {e}")
        print("=" * 60)
        return False

def batch_extract_audio(video_urls, output_dir="audio", audio_format="mp3", quality="128k"):
    """
    批量从多个视频中提取音频
    
    Args:
        video_urls: 视频URL列表
        output_dir: 输出音频文件的目录
        audio_format: 音频格式，默认为mp3
        quality: 音频质量，默认为128k
    """
    print(f"\n" + "=" * 80)
    print(f"开始批量提取音频")
    print(f"总视频数: {len(video_urls)}")
    print(f"输出目录: {output_dir}")
    print(f"音频格式: {audio_format}")
    print(f"音频质量: {quality}")
    print("=" * 80)
    
    success_count = 0
    fail_count = 0
    failed_urls = []
    
    for i, url in enumerate(video_urls, 1):
        print(f"\n" + "-" * 80)
        print(f"处理第 {i}/{len(video_urls)} 个视频")
        print(f"URL: {url}")
        print("-" * 80)
        
        if extract_audio(url, output_dir, audio_format, quality):
            success_count += 1
        else:
            fail_count += 1
            failed_urls.append(url)
    
    print(f"\n" + "=" * 80)
    print("批量提取音频完成!")
    print(f"成功: {success_count} 个")
    print(f"失败: {fail_count} 个")
    
    if failed_urls:
        print("\n失败的URL:")
        for url in failed_urls:
            print(f"  - {url}")
    
    print("=" * 80)

def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="视频音频提取工具",
        formatter_class=argparse.RawTextHelpFormatter
    )
    parser.add_argument(
        "--url", 
        type=str, 
        help="单个视频的URL（支持Bilibili、YouTube等）"
    )
    parser.add_argument(
        "--file", 
        type=str, 
        help="包含视频URL列表的文件路径（每行一个URL）"
    )
    parser.add_argument(
        "--output", 
        type=str, 
        default="audio", 
        help="输出音频文件的目录（默认: audio）"
    )
    parser.add_argument(
        "--format", 
        type=str, 
        default="mp3", 
        help="音频格式（默认: mp3）"
    )
    parser.add_argument(
        "--quality", 
        type=str, 
        default="128k", 
        help="音频质量（默认: 128k）"
    )
    
    args = parser.parse_args()
    
    # 打印欢迎信息
    print("视频音频提取工具 v1.0.0")
    print("支持从Bilibili、YouTube等网站提取音频")
    
    # 检查依赖
    if not install_dependencies():
        print("\n依赖安装失败，退出程序")
        sys.exit(1)
    
    # 处理输入
    if args.url:
        # 单个视频
        extract_audio(args.url, args.output, args.format, args.quality)
    elif args.file:
        # 批量处理
        if not os.path.exists(args.file):
            print(f"\n文件不存在: {args.file}")
            sys.exit(1)
        
        # 读取URL列表
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                urls = [line.strip() for line in f if line.strip()]
            
            if urls:
                batch_extract_audio(urls, args.output, args.format, args.quality)
            else:
                print("\n文件中没有有效的URL")
                sys.exit(1)
        except Exception as e:
            print(f"\n读取文件失败: {e}")
            sys.exit(1)
    else:
        print("\n请指定视频URL或包含URL列表的文件")
        print("使用 --help 查看帮助信息")
        sys.exit(1)

if __name__ == "__main__":
    main()
