#!/usr/bin/env python3
"""Requirements-based checks and C++ / browser-model trace comparison."""
from pathlib import Path
import csv
import json
import random
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'output' / 'build'
EVIDENCE = ROOT / 'evidence'
BUILD.mkdir(parents=True, exist_ok=True)
EVIDENCE.mkdir(exist_ok=True)
CPP = BUILD / 'controller_runner'
DEBOUNCE = BUILD / 'test_debounce'
FIRMWARE = BUILD / 'test_firmware'
subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', '-O2',
                str(ROOT/'tests/controller_runner.cpp'), '-o', str(CPP)], check=True)
subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', '-O2',
                str(ROOT/'tests/test_debounce.cpp'), '-o', str(DEBOUNCE)], check=True)
subprocess.run(['g++', '-std=c++11', '-Wall', '-Wextra', '-Werror', '-O2',
                '-I',str(ROOT/'tests'),str(ROOT/'tests/test_firmware.cpp'),
                '-o',str(FIRMWARE)], check=True)

def e(t, action, value=0):
    return [t, action, value]

def check(index, expected):
    return [index, expected]

READY = {'state':'READY','credit':50,'blue':True,'wash':False}
RUNNING = {'state':'RUNNING','credit':0,'wash':True}
IDLE = {'state':'STANDBY','credit':0,'red':True,'blue':False,'wash':False,'stops':0}
cases = [
    ('T01','Standby LEDs', [e(0,'RESET')], [check(0,IDLE)]),
    ('T02','RUN with less than 50 cents', [e(0,'RESET'),e(10,'COIN',10),e(20,'COIN',20),e(30,'RUN')], [check(3,{'state':'STANDBY','credit':30,'wash':False})]),
    ('T03','Accumulate 20 + 20 + 10 cents', [e(0,'RESET'),e(10,'COIN',20),e(20,'COIN',20),e(30,'COIN',10)], [check(2,{'credit':40,'state':'STANDBY'}),check(3,READY)]),
    ('T04','One 50 cent coin', [e(0,'RESET'),e(1,'COIN',50)], [check(1,READY)]),
    ('T05','Discard surplus when starting', [e(0,'RESET'),e(1,'COIN',20),e(2,'COIN',50),e(3,'RUN')], [check(2,{'credit':70,'state':'READY'}),check(3,{**RUNNING,'remaining':1800000})]),
    ('T06','Reject unsupported 25 cent coin', [e(0,'RESET'),e(1,'COIN',25),e(2,'RUN')], [check(2,IDLE)]),
    ('T07','Ignore coins during active cycle', [e(0,'RESET'),e(1,'COIN',50),e(2,'RUN'),e(3,'COIN',50),e(4,'PAUSE'),e(5,'COIN',20)], [check(3,{**RUNNING,'remaining':1799999}),check(5,{'state':'PAUSED','credit':0,'wash':False})]),
    ('T08','Blue LED blinks every 500 ms', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(499,'TICK'),e(500,'TICK'),e(1000,'TICK')], [check(3,{'blue':True}),check(4,{'blue':False,'wash':True}),check(5,{'blue':True})]),
    ('T09','PAUSE keeps timer counting', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(480000,'PAUSE'),e(960000,'TICK')], [check(3,{'state':'PAUSED','wash':False,'blue':True,'remaining':1320000}),check(4,{'state':'PAUSED','remaining':840000})]),
    ('T10','Resume retains original deadline', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(480000,'PAUSE'),e(960000,'RUN')], [check(4,{**RUNNING,'remaining':840000})]),
    ('T11','Running cycle ends exactly at 30 min', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1799999,'TICK'),e(1800000,'TICK')], [check(3,{**RUNNING,'remaining':1}),check(4,IDLE)]),
    ('T12','Paused cycle also ends at 30 min', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'PAUSE'),e(1800000,'TICK')], [check(4,IDLE)]),
    ('T13','Two STOP presses force stop', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'STOP'),e(2000,'STOP')], [check(3,{'state':'RUNNING','stops':1,'wash':True}),check(4,IDLE)]),
    ('T14','Two STOP presses while paused', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'PAUSE'),e(2000,'STOP'),e(3000,'STOP')], [check(4,{'state':'PAUSED','stops':1}),check(5,IDLE)]),
    ('T15','STOP count survives pause and resume', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'STOP'),e(2000,'PAUSE'),e(3000,'RUN'),e(60000,'STOP')], [check(5,{'stops':1,'state':'RUNNING'}),check(6,IDLE)]),
    ('T16','New cycle clears STOP count', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1,'STOP'),e(2,'STOP'),e(3,'COIN',50),e(4,'RUN'),e(5,'STOP')], [check(6,{'state':'RUNNING','stops':0}),check(7,{'state':'RUNNING','stops':1})]),
    ('T17','Fault stops washing and blinks red', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'FAULT',1),e(1500,'TICK'),e(2000,'TICK')], [check(3,{'state':'ERROR','wash':False,'red':True,'blue':False,'credit':0}),check(4,{'red':False}),check(5,{'red':True})]),
    ('T18','Error is latched until board reset', [e(0,'RESET'),e(1,'FAULT',1),e(2,'FAULT',0),e(3,'COIN',50),e(4,'RUN'),e(5,'STOP'),e(6,'STOP'),e(7,'RESET')], [check(6,{'state':'ERROR','credit':0,'wash':False}),check(7,IDLE)]),
    ('T19','Repeated RUN cannot restart timer', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(900000,'RUN')], [check(3,{**RUNNING,'remaining':900000})]),
    ('T20','Unsigned timer survives clock rollover', [e(4294967040,'RESET'),e(4294967040,'COIN',50),e(4294967040,'RUN'),e(4294968040,'TICK'),e(4296767040,'TICK')], [check(3,{**RUNNING,'remaining':1799000}),check(4,IDLE)]),
    ('T21','Fault has priority over commands', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'BOTH',15)], [check(3,{'state':'ERROR','wash':False})]),
    ('T22','Timeout has priority over resume', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'PAUSE'),e(1800000,'RUN')], [check(4,IDLE)]),
    ('T23','PAUSE has priority over RUN', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'BOTH',3)], [check(3,{'state':'PAUSED','wash':False})]),
    ('T24','STOP has priority over PAUSE', [e(0,'RESET'),e(0,'COIN',50),e(0,'RUN'),e(1000,'BOTH',6)], [check(3,{'state':'RUNNING','stops':1})]),
    ('T25','Unused buttons in standby do nothing', [e(0,'RESET'),e(1,'STOP'),e(2,'PAUSE')], [check(2,IDLE)]),
]

def execute(events):
    trace = ''.join(f'{t} {a} {v}\n' for t,a,v in events)
    cpp = subprocess.run([str(CPP)],input=trace,text=True,capture_output=True,check=True)
    js = subprocess.run(['node',str(ROOT/'tests/js_runner.js')],input=trace,text=True,capture_output=True,check=True)
    c = [json.loads(s) for s in cpp.stdout.splitlines()]
    j = [json.loads(s) for s in js.stdout.splitlines()]
    if c != j:
        for i,(x,y) in enumerate(zip(c,j)):
            if x != y: raise AssertionError(f'Trace mismatch at {events[i]}: C++={x}, JS={y}')
        raise AssertionError('Trace length mismatch')
    return c

rows, all_traces, assertions = [], [], 0
for tid,title,events,expected in cases:
    results = execute(events)
    for index,wanted in expected:
        for key,value in wanted.items():
            got = results[index][key]
            assert got == value, f'{tid} {title}: step {index}, {key}: {got} != {value}'
            assertions += 1
    rows.append({'id':tid,'test':title,'result':'PASS'})
    all_traces.append({'id':tid,'test':title,'events':events,'results':results})
    print(f'PASS {tid}: {title}')

# Seeded exploratory comparison; the independent expected cases above are
# the requirements checks. This trace catches browser/C++ model differences.
rng = random.Random(2353334)
random_events = [e(0,'RESET')]
t = 0
for i in range(5000):
    t += rng.randrange(0,120001)
    action = rng.choice(['COIN','RUN','PAUSE','STOP','TICK','FAULT','RESET','BOTH'])
    value = rng.choice([10,20,50,25]) if action == 'COIN' else rng.randrange(16) if action == 'BOTH' else rng.randrange(2) if action == 'FAULT' else 0
    random_events.append(e(t,action,value))
execute(random_events)
debounce = subprocess.run([str(DEBOUNCE)],text=True,capture_output=True,check=True).stdout.strip()
firmware = subprocess.run([str(FIRMWARE)],text=True,capture_output=True,check=True).stdout.strip()
print(debounce)
print(firmware)
print(f'PASS: {len(cases)} scenarios, {assertions} expected-field assertions, 5001 matching C++/JS trace steps.')

with (EVIDENCE/'test_results.csv').open('w',newline='',encoding='utf-8') as f:
    w=csv.DictWriter(f,fieldnames=['id','test','result']); w.writeheader(); w.writerows(rows)
(EVIDENCE/'test_traces.json').write_text(json.dumps(all_traces,indent=2),encoding='utf-8')
(EVIDENCE/'random_trace.txt').write_text(''.join(f'{t} {a} {v}\n' for t,a,v in random_events),encoding='utf-8')
summary = {
    'scenario_count':len(cases),'expected_field_assertions':assertions,
    'cpp_js_matching_trace_steps':5001,'debounce_checks':13,'firmware_adapter_checks':15,
    'status':'PASS','seed':2353334,
    'scope':'Host C++ controller and JavaScript model; no physical board test.'
}
(EVIDENCE/'test_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
(EVIDENCE/'test_console.txt').write_text('\n'.join(f"PASS {r['id']}: {r['test']}" for r in rows)+'\n'+debounce+'\n'+firmware+f'\nPASS: {len(cases)} scenarios, {assertions} expected-field assertions, 5001 matching C++/JS trace steps.\n',encoding='utf-8')
