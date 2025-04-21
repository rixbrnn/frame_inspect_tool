# frame_inspect_tool
A tool to compare graphics rendered with upscaling or frame generation to their source using SSIM.

# setup

Install python and then install the dependencies with

`pip install -r requirements.txt`

Important:
Is very easy to move the mouse around while taking screenshots. This tool requires the screenshot to be at the exact same position as before,
therefore I recommend only using it on scenes in which you can garantee there was no mouse movement from you. Alternatively, if the game you are testing supports
graphics preview feature (such as God of War: Ragnarok) while in the menu settings, that ideal for taking screenshots.
Alternatively, you can take the screenshots disabling the mouse to ensure there wont be any movement.
You must find a spot that does not have variable visuals, it needs to be a still frame.
Also, if the game has a "breathing" camera you must disable it or find a situation in which that is not active.
Otherwise your screenshots might not be a fair comparison.