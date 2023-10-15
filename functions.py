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

# STREAMLIT
import streamlit as st


def GetVoices(targetLang,text,voiceId,apiKey,messages):
  headers = {'accept': 'audio/mpeg','xi-api-key': apiKey,'Content-Type': 'application/json'}
  stab  = 0.25
  boost = 0.75
  json_data = {'text': text,'model_id': 'eleven_multilingual_v1','language_id': 'it', 'voice_settings': {'stability': stab,'similarity_boost': boost}}


  audioByte = requests.post('https://api.elevenlabs.io/v1/text-to-speech/'+voiceId, headers=headers, json=json_data).content
  return audioByte

def FromVoiceListToSelectList(voiceList):
  voiceNameList = []
  voiceDescList = []
  for i,voice in enumerate(voiceList):
    voiceNameList.append(voice['name'])
    desc = voice['description']
    #print(desc)
    if 'description' in desc.keys() and 'use case' in desc.keys() and 'accent' in desc.keys():
      descString ='{} accent {} {}, with a {} voice, adapt for {} '.format(desc['accent'],desc['age'],desc['gender'],desc['description'],desc['use case'])
    else:
      #print(i)
      descString ='{} accent {} {}, with a {} voice, adapt for {} '.format('general','general','unkown','common','general purpose')
    voiceDescList.append(descString)
  
  return voiceNameList,voiceDescList

def FromVoiceNameToIdx(name,voiceNameList):
  idx=0
  for i,voiceName in enumerate(voiceNameList):
    if name == voiceName:
      idx=i
      break
  return idx
    



def GetVoiceList(apiKey):
  headers  = {'accept': 'application/json','xi-api-key': apiKey}
  response = requests.get('https://api.elevenlabs.io/v1/voices', headers=headers)
  voices   = json.loads(response.content)['voices']

  voiceList = []
  for voice in voices:
    voiceList.append({'name':voice['name'],'id':voice['voice_id'],'description':voice['labels']})

  return voiceList

def GetAnswer(messages,question,temp):
  messages.append({"role": "user", "content": question})
  response = openai.ChatCompletion.create(model="gpt-4",messages=messages,temperature=temp)
  output = response['choices'][0]['message']['content']
  messages.append({"role": "assistant", "content": output})
  return messages

def InitiMessage(promptSystem):
  messages = []
  messages.append({"role": "system", "content": promptSystem})
  return messages
