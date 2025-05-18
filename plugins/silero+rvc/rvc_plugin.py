import io
import re
import os
import time
import requests
import subprocess
import numpy as np
import soundfile as sf
import shutil
from pydub import AudioSegment
from LAV_utils import download_and_extract_zip
from .inferrvc import load_torchaudio
from .inferrvc import RVC
from pluginInterface import TTSPluginInterface
import gradio as gr

class SileroRVCPlugin(TTSPluginInterface):
    current_module_directory = os.path.dirname(__file__)
    SILERO_OUTPUT_FILENAME = os.path.join(current_module_directory, "silero_output.wav")
    RVC_OUTPUT_FILENAME = os.path.join(current_module_directory, "rvc_output.wav")
    rvc_model_dir = os.path.join(current_module_directory, "rvc_model_dir")
    rvc_index_dir = os.path.join(current_module_directory, "rvc_index_dir")
    
    # Silero settings
    SILERO_URL_LOCAL = "127.0.0.1"
    SILERO_PORT = "8435"
    silero_server_started = False
    current_language = "v3_en.pt"  # Default language
    current_speaker = "en_0"  # Default speaker
    session_path = os.path.join(current_module_directory, "session")
    
    # RVC settings
    rvc_model_name = 'Neurosama-V3-copy7.pth'
    use_rvc = True
    transpose = 0
    index_rate = 0.75
    protect = 0.5

    def init(self):
        # Setup RVC environment
        os.environ['RVC_MODELDIR'] = self.rvc_model_dir
        os.environ['RVC_INDEXDIR'] = self.rvc_index_dir
        os.environ['RVC_OUTPUTFREQ'] = '44100'
        os.environ['RVC_RETURNBLOCKING'] = 'False'

        if not os.path.exists(os.path.join(self.rvc_model_dir, self.rvc_model_name)):
            self.download_model_from_url(
                "https://huggingface.co/zAnonymousWizard/genshinqiqi/resolve/main/qiqigenshin.zip?download=true")

        self.model = RVC(self.rvc_model_name)
        self.update_rvc_model_list()
        
        # Start Silero server and initialize session
        self.start_silero_server()
        self.init_session(self.session_path)
        # Set default language
        self.set_silero_language(self.current_language)

    def start_silero_server(self):
        if self.silero_server_started:
            return
            
        command = f"python -m silero_api_server -p {self.SILERO_PORT}"
        subprocess.Popen(command, shell=True)
        self.silero_server_started = True

    def init_session(self, session_path):
        url = f"http://{self.SILERO_URL_LOCAL}:{self.SILERO_PORT}/tts/session"
        while True:
            try:
                data = {"path": session_path}
                response = requests.post(url, json=data, timeout=2)
                if response.status_code == 200:
                    print("Silero session initialized successfully")
                    break
            except:
                print("Waiting for silero to start...")
                time.sleep(0.5)

    def set_silero_language(self, language_id):
        """Set language for Silero TTS"""
        url = f"http://{self.SILERO_URL_LOCAL}:{self.SILERO_PORT}/tts/language"
        data = {"id": language_id}
        try:
            response = requests.post(url, json=data, timeout=2)
            response.raise_for_status()
            self.current_language = language_id
            return True
        except Exception as e:
            print(f"Error setting Silero language: {e}")
            return False

    def synthesize(self, text):
        text = self.preprocess_text(text)
        
        # Generate speech with Silero
        url = f"http://{self.SILERO_URL_LOCAL}:{self.SILERO_PORT}/tts/generate"
        data = {
            "speaker": self.current_speaker,
            "text": text,
            "session": ""
        }
        
        try:
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            with open(self.SILERO_OUTPUT_FILENAME, "wb") as f:
                f.write(response.content)
                
            # Process with RVC if enabled
            if self.use_rvc:
                aud, sr = load_torchaudio(self.SILERO_OUTPUT_FILENAME)
                paudio1 = self.model(aud, f0_up_key=self.transpose,
                                    output_volume=RVC.MATCH_ORIGINAL, 
                                    index_rate=self.index_rate, 
                                    protect=self.protect)
                paudio1_cpu = paudio1.cpu().numpy()
                sf.write(self.RVC_OUTPUT_FILENAME, paudio1_cpu, 44100)
                audio = AudioSegment.from_wav(self.RVC_OUTPUT_FILENAME)
            else:
                audio = AudioSegment.from_wav(self.SILERO_OUTPUT_FILENAME)
                
            buffer = io.BytesIO()
            audio.export(buffer, format='wav')
            return buffer.getvalue()
            
        except Exception as e:
            print(f"Error in synthesis pipeline: {e}")
            return None

    def create_ui(self):
        language_names = self.get_langauges()
        speaker_names = self.get_speaker_names()
        self.current_speaker = speaker_names[0]
        
        with gr.Accordion(label="Silero + RVC Options", open=False):
            # Silero options
            with gr.Row():
                self.language_dropdown = gr.Dropdown(
                    choices=language_names,
                    value=self.current_language,
                    label="Language: "
                )
                self.speaker_dropdown = gr.Dropdown(
                    choices=speaker_names,
                    value=self.current_speaker,
                    label="Speaker: "
                )
            
            # RVC options
            with gr.Row():
                self.use_rvc_checkbox = gr.Checkbox(label='Use RVC', value=self.use_rvc)
                self.rvc_model_dropdown = gr.Dropdown(
                    label="RVC models:",
                    choices=self.rvc_model_names,
                    value=self.rvc_model_name if self.rvc_model_names else None,
                    interactive=True
                )
                self.refresh_button = gr.Button("Refresh", variant="primary")

            with gr.Row():
                self.download_model_input = gr.Textbox(label="Model url:")
                self.download_button = gr.Button("Download")
            gr.Markdown("You can find models here: https://voice-models.com/top")

            with gr.Column():
                self.transpose_slider = gr.Slider(
                    value=self.transpose,
                    minimum=-24, maximum=24, step=1,
                    label='Transpose'
                )
                self.index_rate_slider = gr.Slider(
                    value=self.index_rate,
                    minimum=0, maximum=1, step=0.01,
                    label='Index Rate'
                )
                self.protect_slider = gr.Slider(
                    value=self.protect,
                    minimum=0, maximum=0.5, step=0.01,
                    label='Protect'
                )

            # Connect UI events
            self.language_dropdown.input(
                self.on_language_change,
                inputs=[self.language_dropdown],
                outputs=[self.speaker_dropdown]
            )
            self.speaker_dropdown.input(
                self.on_speaker_change,
                inputs=[self.speaker_dropdown]
            )
            self.rvc_model_dropdown.input(
                self.on_rvc_model_change,
                inputs=[self.rvc_model_dropdown],
                outputs=[]
            )
            self.refresh_button.click(
                self.on_refresh,
                outputs=[self.rvc_model_dropdown]
            )
            self.use_rvc_checkbox.change(
                self.on_use_rvc_click,
                inputs=self.use_rvc_checkbox,
                outputs=None
            )
            self.transpose_slider.change(
                self.on_transpose_change,
                inputs=self.transpose_slider,
                outputs=None
            )
            self.index_rate_slider.change(
                self.on_index_rate_change,
                inputs=self.index_rate_slider,
                outputs=None
            )
            self.protect_slider.change(
                self.on_protect_change,
                inputs=self.protect_slider,
                outputs=None
            )
            self.download_button.click(
                self.download_model_from_url,
                inputs=self.download_model_input
            )

    def get_langauges(self):
        """Get available Silero languages"""
        url = f"http://{self.SILERO_URL_LOCAL}:{self.SILERO_PORT}/tts/language"
        try:
            response = requests.get(url, timeout=20)
            return response.json()
        except Exception as e:
            print(f"Error getting languages: {e}")
            # Fallback values
            return ["v3_en.pt", "v3_1_ru.pt"]

    def get_speakers(self):
        """Get all available Silero speakers"""
        url = f"http://{self.SILERO_URL_LOCAL}:{self.SILERO_PORT}/tts/speakers"
        try:
            response = requests.get(url, timeout=20)
            return response.json()
        except Exception as e:
            print(f"Error getting speakers: {e}")
            # Fallback speakers
            return [{"name": "en_0"}, {"name": "en_1"}, {"name": "en_2"}, {"name": "aidar"}, {"name": "baya"}, {"name": "xenia"}]

    def get_speaker_names(self):
        """Get names of available Silero speakers"""
        return [speaker['name'] for speaker in self.get_speakers()]

    def on_language_change(self, choice):
        """Handle language change event"""
        url = f"http://{self.SILERO_URL_LOCAL}:{self.SILERO_PORT}/tts/language"
        data = {"id": choice}
        try:
            response = requests.post(url, json=data, timeout=2)
            response.raise_for_status()
            self.current_language = choice
            print(f"Changed language to: {choice}")
            speaker_names = self.get_speaker_names()
            self.current_speaker = speaker_names[0]
            return gr.update(choices=speaker_names, value=self.current_speaker)
        except Exception as e:
            print(f"Error changing language: {e}")
            return gr.update(choices=[], value=None)

    def on_speaker_change(self, choice):
        """Handle speaker change event"""
        self.current_speaker = choice
        print(f"Changed speaker to: {choice}")

    def on_transpose_change(self, value):
        self.transpose = value

    def on_index_rate_change(self, value):
        self.index_rate = value

    def on_protect_change(self, value):
        self.protect = value

    def on_use_rvc_click(self, use):
        self.use_rvc = use

    def on_rvc_model_change(self, choice):
        self.rvc_model_name = choice
        self.model = RVC(self.rvc_model_name)

    def on_refresh(self):
        self.update_rvc_model_list()
        return gr.update(choices=self.rvc_model_names)

    def update_rvc_model_list(self):
        self.rvc_model_names = []
        if os.path.exists(self.rvc_model_dir):
            for name in os.listdir(self.rvc_model_dir):
                if name.endswith(".pth"):
                    self.rvc_model_names.append(name)

    def download_model_from_url(self, url):
        folder_path = download_and_extract_zip(
            url, extract_to=self.current_module_directory)

        # Find the .pth file and get its base name
        pth_file_path = None
        base_name = None
        for file in os.listdir(folder_path):
            if file.endswith('.pth'):
                base_name = os.path.splitext(file)[0]
                pth_file_path = os.path.join(folder_path, file)
                break

        if pth_file_path and base_name:
            # Look for the corresponding .index file
            for file in os.listdir(folder_path):
                if file.endswith('.index'):
                    original_index_file_path = os.path.join(folder_path, file)
                    new_index_file_path = os.path.join(
                        folder_path, base_name + '.index')
                    os.rename(original_index_file_path, new_index_file_path)

                    # Move the .pth file
                    os.makedirs(self.rvc_model_dir, exist_ok=True)
                    shutil.move(pth_file_path, os.path.join(
                        self.rvc_model_dir, os.path.basename(pth_file_path)))

                    # Move the .index file
                    os.makedirs(self.rvc_index_dir, exist_ok=True)
                    shutil.move(new_index_file_path, os.path.join(
                        self.rvc_index_dir, os.path.basename(new_index_file_path)))

                    # Remove the folder once done
                    try:
                        os.rmdir(folder_path)
                    except OSError:
                        shutil.rmtree(folder_path)
                    break
            else:
                print(f"No .index file found for {base_name}")
        else:
            print("No .pth file found in the folder.")

    def preprocess_text(self, text):
        print(f"replacing decimal point with the word point.")
        print(f"original:) {text}")

        pattern = r'\b\d*\.\d+\b'

        def replace_match(match):
            decimal_number = match.group(0)
            return decimal_number.replace('.', ' point ')

        replaced_text = re.sub(pattern, replace_match, text)
        print(f"replaced_text: {replaced_text}")
        
        return replaced_text