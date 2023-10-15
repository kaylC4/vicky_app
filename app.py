
# CHATGPT
import openai

# VOICES AND MUSIC
from elevenlabs import generate, play
from elevenlabs import set_api_key
from pydub import AudioSegment, effects
from pydub.silence import detect_nonsilent

# UTILS
import io
import os
import json
import IPython.display as ipd
import requests
import time
from datetime import date



# STREAMLIT
import streamlit as st

# FUNCTIONS
from functions import *



################################################################################
################################### INIT #######################################
################################################################################

############################# SESSION STATE ####################################

if 'apiKeys' not in st.session_state:
    st.session_state['apiKeys'] = {'openAI':'','eleven':''}

if 'option' not in st.session_state:
    st.session_state['option'] = {}
    st.session_state['option']['temperature'] = 0.5
    st.session_state['option']['voice']       = {}
    st.session_state['option']['system']      = "Tu sei un intelligenza artificiale senza pregiudizi e preconcetti rispetto a generi, sessualità e orientamento politico. Sei spiritosa e con un humor tagliente. Dai sempre risposte molto concise senza dilungarti troppo, ma senza risultare sgarbata."

if "openai_model" not in st.session_state:
    st.session_state["openai_model"] = "gpt-4"

if 'messages' not in st.session_state:
    st.session_state['messages'] = InitiMessage(st.session_state['option']['system'])

############################## SAVE FOLDERS ####################################

if not os.path.exists(os.path.join('audiofiles')):
  os.mkdir(os.path.join('audiofiles'))

if not os.path.exists(os.path.join('audiofiles',str(date.today()))):
  os.mkdir(os.path.join('audiofiles',str(date.today())))

savePath = os.path.join('audiofiles',str(date.today()))

################################################################################
################################### SETTING ####################################
################################################################################

with st.sidebar:
  st.markdown('## Settings')

  st.markdown('### API Keys')
  st.session_state['apiKeys']['openAI'] = st.text_input(label='OpenAi',key='OpenAiKey',   placeholder = 'OpenAI API Key',    value = "")
  if st.session_state['apiKeys']['openAI']:
    openai.api_key = st.session_state['apiKeys']['openAI']

  st.session_state['apiKeys']['eleven'] = st.text_input(label='ElevenLab',key='ElevenLabKey', placeholder =' ElevenLab API Key', label_visibility="collapsed", value = "")
  if st.session_state['apiKeys']['eleven'] and st.session_state['apiKeys']['openAI']:
      st.markdown('### Voices')

      # Get voice from elevenlabs
      voiceList = GetVoiceList(st.session_state['apiKeys']['eleven'])

      # Exctract name and description
      voiceNameList,voiceDescList = FromVoiceListToSelectList(voiceList)

      # Select your voice and get relative description
      name = st.selectbox(label='Select a Voice',key='voiceSelect',label_visibility="collapsed",placeholder="Select a voice",options=voiceNameList,index=None)
      st.session_state['option']['voice'] = voiceList[FromVoiceNameToIdx(name,voiceNameList)]
      st.markdown(voiceDescList[FromVoiceNameToIdx(name,voiceNameList)])

  st.markdown('### Creativity')
  st.session_state['option']['temperature'] = st.slider(label='Creativity',key='creativity',label_visibility="collapsed", min_value=0.0, max_value=1.0, value=st.session_state['option']['temperature'],step=0.1)

  st.markdown('### System Personality')
  systemPrompt = st.text_area(label="Personality",key='personality',label_visibility="collapsed",placeholder=st.session_state['option']['system'])
  if systemPrompt:
    st.session_state['option']['system'] = systemPrompt
    st.session_state['messages']         = InitiMessage(st.session_state['option']['system'])


################################################################################
##################################### MAIN #####################################
################################################################################

st.title('Vicky :astronaut:')

if st.session_state['option']['voice'] and st.session_state['option']['system']:

  full_response=''

  for message in st.session_state.messages:
      with st.chat_message(message["role"]):
          st.markdown(message["content"])

  if prompt := st.chat_input("Urgenze?"):
      st.session_state.messages.append({"role": "user", "content": prompt})
      with st.chat_message("user"):
          st.markdown(prompt)

      with st.chat_message("assistant"):
          message_placeholder = st.empty()
          full_response = ""
          for response in openai.ChatCompletion.create(
              model=st.session_state["openai_model"],
              messages=[
                  {"role": m["role"], "content": m["content"]}
                  for m in st.session_state.messages
              ],
              stream=True,
          ):
              full_response += response.choices[0].delta.get("content", "")
              message_placeholder.markdown(full_response + "▌")
          message_placeholder.markdown(full_response)



      st.session_state.messages.append({"role": "assistant", "content": full_response})

  # Voice File
  if full_response:
    # Get and display
    audio = GetVoices('it',full_response,st.session_state['option']['voice']['id'],st.session_state['apiKeys']['eleven'] ,st.session_state.messages)
    st.audio(audio, format='audio/mp3')

    # Save
    audioName = os.path.join(savePath,'voice_'+prompt+'.mp3')
    audioSeg  = AudioSegment.from_file(io.BytesIO(audio))
    audioSeg.export(audioName, format="mp3")



