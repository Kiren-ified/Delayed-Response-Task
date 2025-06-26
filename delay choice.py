import pandas as pd
from psychopy.gui import DlgFromDict
from psychopy.visual import Window, TextStim, ImageStim, Rect, TextBox
from psychopy.core import Clock, quit, wait
from psychopy.event import Mouse
from psychopy.hardware.keyboard import Keyboard
from psychopy import event
import random
from psychopy import visual, core, event, gui

### DIALOG BOX ROUTINE ###
exp_info = {'participant_nr': '', 'age': '','condition':['future','past']}
dlg = DlgFromDict(exp_info)

# If pressed Cancel, abort!
if not dlg.OK:
    quit()

# Initialize a fullscreen window with my monitor (HD format) size
# and my monitor specification called "samsung" from the monitor center
win = Window(size=(1920, 1080), fullscr=False, monitor='samsung')

# Also initialize a mouse, although we're not going to use it
mouse = Mouse(visible=False)

# Initialize a (global) clock
clock = Clock()

# Initialize Keyboard
kb = Keyboard()
kb.clearEvents()

### WELCOME ROUTINE ###
# Create a welcome screen and show for 2 seconds
welcome_txt_stim = TextStim(win, text="Welcome to this experiment!", color=(1, 0.6, 0.6), font='Calibri')
welcome_txt_stim.draw()
win.flip()
wait(2)


trials = pd.read_csv('cues.csv')

# rename so it matches our code
trials = trials.rename(columns={
    'offer amount':   'delayed_amount',
    'offer delay':    'delay',
    'cue':            'cue_text'
})

# Forward‐fill so that every row has a numeric amount & a delay string
trials['delayed_amount'] = trials['delayed_amount'].ffill()
trials['delay']          = trials['delay'].ffill()

# add the immediate option
trials['immediate_amount'] = 20

# 1st shuffle: group assignment
trials = trials.sample(frac=1, random_state=42).reset_index(drop=True)

# compute split point
n    = len(trials)
half = n // 2        

# assign exactly half cued / half no-cue
trials.loc[:half-1, 'cue_present'] = True
trials.loc[ half:,  'cue_present'] = False

# final shuffle
trials = trials.sample(frac=1, random_state=99).reset_index(drop=True)

# prepare columns for responses
trials['resp'] = ''
trials['rt']   = 0.0

#Set up stimuli
fixation = visual.TextStim(win, text='+', height=0.2, color='black')
instr = visual.TextStim(
    win,
    text="Use ← for $20 today\nUse → for the delayed amount\n\n(Press SPACE to begin)",
    color='black',
    wrapWidth=1.5,
    height=0.07,
    alignText='center'
)   

instr_text = """
You will make choices between monetary amounts.
On each trial you will choose between whether you prefer an immediate amount
or an amount available after a delay.
Some trials will have future events displayed
You can click the offer you prefer
Use left arrow to choose $20 today
Use right arrow to choose the delayed amount
(Press SPACE to begin)
"""
instr = visual.TextStim(
    win,
    text=instr_text,
    color='black',
    wrapWidth=1.5,
    height=0.07,
    alignText='center'
)
instr.draw()
win.flip()

# Initialize keyboard and wait for response
kb = Keyboard()
while True:
    keys = kb.getKeys()
    if 'space' in keys:
        # The for loop was optional
        for key in keys:
            print(f"The {key.name} key was pressed within {key.rt:.3f} seconds for a total of {key.duration:.3f} seconds.")
        break  # break out of the loop!

# Wait for spacebar before starting your trials
delayed_with_cue    = 0
delayed_without_cue = 0
trial_clock = core.Clock()

for idx, row in trials.iterrows():
    # fixation
    fixation.draw()
    win.flip()
    wait(0.5)

    # parse amount & delay
    amt        = int(row['delayed_amount'])
    delay_str  = str(row['delay']).split()[0]
    days       = int(delay_str)

    left_txt   = "$20 today"
    right_txt  = f"${amt} in {days} days"

    # make stimuli
    stim_left  = visual.TextStim(win, text=left_txt,  pos=(-0.5, 0), height=0.1)
    stim_right = visual.TextStim(win, text=right_txt, pos=( 0.5, 0), height=0.1)

    cue_stim = None
    if row['cue_present']:
        cue_stim = visual.TextStim(win, text=row['cue_text'],
                                   pos=(0,0.6), color=(1, 0.6, 0.6), height=0.08)

    # draw & flip
    stim_left.draw()
    stim_right.draw()
    if cue_stim: cue_stim.draw()
    win.flip()

    trial_clock.reset()
    key, rt = event.waitKeys(
        keyList=['left','right'],
        timeStamped=trial_clock
    )[0]
    
     # map & record
    resp = 'immediate' if key=='left' else 'delayed'
    trials.at[idx, 'key']  = key
    trials.at[idx, 'rt']   = rt
    trials.at[idx, 'resp'] = resp
    
    #update counters
    if resp=='delayed':
        if row['cue_present']:
            delayed_with_cue    += 1
        else:
            delayed_without_cue += 1

# console feedback
print(f"Key: {key}, RT: {rt:.3f}s → Response: {resp}")


# --- THANK YOU SCREEN ---
thank_you = visual.TextStim(
    win,
    text="Thank you for participating!",
    color=(1, 0.6, 0.6),
    height=0.1,
    alignText='center'
)
thank_you.draw()
win.flip()
wait(2)

txt = f""" 
Your reaction times are as follows:

    Delayed with cue: {delayed_with_cue} / 30
    Delayed without cue: {delayed_without_cue} / 30
\
"""
result = TextStim(win, txt)
result.draw()
win.flip()
wait(2)

#summary
print(f"Delayed WITH cue:    {delayed_with_cue} / 30")
print(f"Delayed WITHOUT cue: {delayed_without_cue} / 30")
trials.to_csv(f"sub-{exp_info['participant_nr']}_results.csv", index=False)
win.close()
quit()