from mido import MidiFile

def getMidiOutput(str):
    mid = MidiFile(str)
    mididict = []
    output = []

    # Put all note on/off in midinote as dictionary.
    for i in mid:
        if i.type == 'note_on' or i.type == 'note_off':
            mididict.append(i.dict())
    # change time values from delta to relative time.
    mem1=0
    for i in mididict:
        time = i['time'] + mem1
        i['time'] = time
        mem1 = i['time']
    # make every note_on with 0 velocity note_off
        if i['type'] == 'note_on' and i['velocity'] == 0:
            i['type'] = 'note_off'
    # put note, starttime, stoptime, as nested list in a list. # format is [type, note, time, channel]
        mem2=[]
        if i['type'] == 'note_on':
            mem2.append(i['type'])
            mem2.append(i['note'])
            mem2.append(i['time'])
            mem2.append(i['channel'])
            output.append(mem2)
    # put timesignatures
        if i['type'] == 'time_signature':
            mem2.append(i['type'])
            mem2.append(i['numerator'])
            mem2.append(i['denominator'])
            mem2.append(i['time'])
            output.append(mem2)
    # viewing the midimessages.
    return output