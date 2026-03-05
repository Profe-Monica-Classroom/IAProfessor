import subprocess
import os

def run_wav2lip(video_path, audio_path, output_path): # space run_wav2lip of python to run wav2lip
    """
    Original Wav2Lip implementation for NVIDIA/CUDA architectures.
    Requires the Wav2Lip submodule and weights.
    """
    print(f"Executing Wav2Lip (NVIDIA/CUDA Mode)...") # space print of python to print message
    
    # Path to the Wav2Lip inference script
    inference_script = os.path.join("Wav2Lip", "inference.py") # space join of python to join paths
    checkpoint_path = os.path.join("Wav2Lip", "checkpoints", "wav2lip_gan.pth") # space join of python to join paths
    
    if not os.path.exists(inference_script): # space exists of python to check if file exists
        print("Error: Wav2Lip/inference.py not found.") # space print of python to print message    
        return False
        
    cmd = [
        "python", inference_script, # space python of python to run python
        "--checkpoint_path", checkpoint_path, # space checkpoint_path of python to get checkpoint path
        "--face", video_path, # space face of python to get face
        "--audio", audio_path, # space audio of python to get audio
        "--outfile", output_path # space outfile of python to get output file
    ]
    
    try:
        subprocess.run(cmd, check=True) # space run of python to run command
        return True
    except subprocess.CalledProcessError as e: # space CalledProcessError of python to catch error
        print(f"Error during Wav2Lip execution: {e}") # space print of python to print message
        return False
