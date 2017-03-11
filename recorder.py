## Records audio, finds frequencies and estimates pitches
# Author: Shreya Prakash

import pyaudio
import wave
import scipy.io.wavfile as wavfile
import numpy as np
import math

class Recorder(object):

    def __init__(self, duration):
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 2
        self.RATE = 44100
        self.CHUNK = 1024
        self.RECORD_SECONDS = duration
        self.WAVE_OUTPUT_FILENAME = "userCEC.wav"
        self.original_file = "" # need to have original file
        self.frames = []

    # used some code from https://gist.github.com/mabdrabo/8678538
    def record(self):

        audio = pyaudio.PyAudio()
         
        # start Recording
        stream = audio.open(format=self.FORMAT, channels=self.CHANNELS,
                        rate=self.RATE, input=True,
                        frames_per_buffer=self.CHUNK)
        print ("recording...")

        # records
        for i in range(0, int(self.RATE / self.CHUNK * self.RECORD_SECONDS)):
            data = stream.read(self.CHUNK)
            audio_data = np.fromstring(data, np.int16)


            # checks if has sound when recording
            def hasSound(data):
              NOISE_THRESHOLD = 30
              if abs(np.average(data)) > NOISE_THRESHOLD:
                return True


            sound = hasSound(audio_data) 
            # if there is sound will print loud otherwise no sound

            if sound:
                print ("loud")
            else:
                print ("no sound")
            self.frames.append(data)
        print ("finished recording")

        # stop Recording
        stream.stop_stream()
        stream.close()
        audio.terminate()

        # creates wave file
        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.frames))
        waveFile.close()
        return (self.WAVE_OUTPUT_FILENAME)

    # used some code from:
    # https://github.com/aubio/aubio/blob/master/python/demos/demo_pitch.py
    def findFrequencies(self, filename, duration):
        from numpy import array, ma
        from aubio import source, pitch

        duration = self.RECORD_SECONDS

        downsample = 1
        samplerate = 44100 // downsample

        win_s = 4096 // downsample # fft size
        hop_s = 512  // downsample # hop size

        s = source(filename, samplerate, hop_s)
        samplerate = s.samplerate
        tolerance = 0.9

        # algorithm to find pitches
        pitch_o = pitch("yin", win_s, hop_s, samplerate)

        # will be midi freq
        pitch_o.set_unit("midi")
        pitch_o.set_tolerance(tolerance)

        pitches = []
        confidences = []

        total_frames = 0

        # finding the freq
        while True:
            samples, read = s()
            pitch = pitch_o(samples)[0]
            confidence = pitch_o.get_confidence()
            # only want when confident
            if confidence < 0.8: pitch = None
            pitches += [pitch]
            confidences += [confidence]
            total_frames += read
            if read < hop_s: break

        skip = 1

        # adding it to the array
        pitches = array(pitches[skip:])
        confidences = array(confidences[skip:])
        length = ((len(pitches)-1)/duration)
        times = [t/length for t in range(len(pitches))]
        newPitches = []
        simplePitches = []
        simpleTimes = []

        # rounds all the pitches
        for i in range(len(pitches)):
            if pitches[i] == None:
                continue
            else:
                roundedPitch = (np.rint(pitches[i]))
                newPitches.append(roundedPitch)

        # finds the most frequent pitche twice every 250 milliseconds
        for time in range(len(times)):
            if (int((times[time]%1)*100)%25) == 0:
                simpleTimes.append(times[time])
                avgPitch = np.rint(np.median(newPitches[:time+1]))
                (avgPitch, times[time])
                simplePitches.append(avgPitch)
        
        return (simpleTimes, simplePitches)

    # finds the differences between pitches
    def findDifference(self, timesorig, times, freqorig, freqother):

        diffTimes = []
        stepsDiff = []

        # will iterate over the song of lesser time
        if len(timesorig) <= len(times):
            lesserTimes = timesorig
        else:
            lesserTimes = times
        
        # will check if the freqs are not the same, and
        # if they are not will add them to diff
        for i in range(len(lesserTimes)):
            if freqorig[i] != freqother[i]:
                diffTimes.append(lesserTimes[i])
                if freqorig[i] > freqother[i]:
                    lowerNote = freqother[i]
                    higherNote = freqorig[i]
                else:
                    lowerNote = freqorig[i]
                    higherNote = freqother[i]

                # will be finding the note values of these pitches
                noteLower = lowerNote%12 + 1
                noteHigher = higherNote%12 + 1

                # check if the note are diff or the same
                stepsDiff.append(abs(noteHigher-noteLower))

        return diffTimes, stepsDiff

    # gets the corressponding note values
    def getNotes(self, pitches):

        # initialize list
        newNotes = [None for val in pitches]
        totalNotes = len(pitches)

        for i in range(totalNotes):
            # if no value, 0
            if math.isnan(pitches[i]):
                newNotes[i] = 0

            # if it is silent, 0
            elif pitches[i] == 0:
                newNotes[i] = 0

            # otherwise find the corresponding note,
            # add 1 so silence and C are not same
            else:
                pitch = int(pitches[i])
                midiToNote = pitch%12
                newNotes[i] = (midiToNote + 1)
                
        return newNotes
