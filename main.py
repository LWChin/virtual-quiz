#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Jun 11 17:18:54 2022

@author: chenyuchun
"""

import cv2
import csv
import cvzone
import time
from cvzone.HandTrackingModule import HandDetector
import numpy as np

cap = cv2.VideoCapture(0)
cap.set(3,1300)
cap.set(4,720)
detector = HandDetector(detectionCon=0.8)

class MCQ():
    def __init__(self,data):
        self.qindex = data[0]
        self.question = data[1]
        self.choice1 = data[2]
        self.choice2 = data[3]
        self.choice3 = data[4]
        self.choice4 = data[5]
#        self.answer = int(data[6])
        self.userAns = None
    
    
    def update(self, cursor, bboxs, qNo, qTotal):
        
        for x, bbox in enumerate(bboxs):
            x1, y1, x2, y2 = bbox
            if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
                if x <= 3:  # 正常作答
                    self.userAns = x + 1
                else:  #選上一題或下一題
                    if x == 4:
                        if qNo-1 < 0:
                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), cv2.FILLED)
                        else:
                            qNo -= 1
                    elif x == 5:
                        if qNo+1 > qTotal:
                            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), cv2.FILLED)
                        else:
                            qNo += 1
                    elif x == 6:
                        qNo += 1

        return qNo
    
pathCSV = "Quiz.csv"
with open(pathCSV, newline='\n') as f:
    reader = csv.reader(f)
    dataAll = list(reader)[1:]
    
#print(dataAll)
#Create Object for each MCQ
mcqList= []
for q in dataAll:
    mcqList.append(MCQ(q))

print("Total MCQ Objects Created:", len(mcqList))

print(len(mcqList))
qNo_list = [i for i in range(len(mcqList))]
np.random.shuffle(qNo_list)
qNo = 0
qTotal = len(dataAll)

def check(cursor, bboxs, qNo):
    for x, bbox in enumerate(bboxs):
        x1, y1, x2, y2 = bbox
        if x1 < cursor[0] < x2 and y1 < cursor[1] < y2:
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), cv2.FILLED)
            if x == 0:  # 再次檢查
                qNo -= 1
            elif x == 1:
                qNo += 1
    return qNo

while True:
    success, img = cap.read()
    img = cv2.flip(img,180)
    hands, img = detector.findHands(img, flipType=False)
    
    if qNo < qTotal:
#        mcq = mcqList[qNo]
        q_index = qNo_list[qNo]
        mcq = mcqList[q_index]
        
        img, bbox = cvzone.putTextRect(img, mcq.question,[50,100],4,2, offset=20, border=5)
        img, bbox1 = cvzone.putTextRect(img, mcq.choice1,[50,250],4,2, offset=20, border=5)
        img, bbox2 = cvzone.putTextRect(img, mcq.choice2,[500,250],4,2, offset=20, border=5)
        img, bbox3 = cvzone.putTextRect(img, mcq.choice3,[50,400],4,2, offset=20, border=5)
        img, bbox4 = cvzone.putTextRect(img, mcq.choice4,[500,400],4,2, offset=20, border=5)
        img, bbox5 = cvzone.putTextRect(img, "Prev",[1000,250],4,2, offset=20, border=5)
        img, bbox6 = cvzone.putTextRect(img, "Next",[1000,400],4,2, offset=20, border=5)
        
        cv2.putText(img, "Answer:",(1000,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        cv2.putText(img, str(mcq.userAns),(1150,50), cv2.FONT_HERSHEY_SIMPLEX, 1.0, (255, 255, 255))
        
        
        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8] #8:食指最上面的點的編號
            length, info = detector.findDistance(lmList[8], lmList[12]) #12:中指
#            print(length)
            if length < 30:
                qNo = mcq.update(cursor, [bbox1, bbox2, bbox3, bbox4, bbox5, bbox6], qNo, qTotal)
                print(mcq.userAns)
                if mcq.userAns is not None:
                    time.sleep(0.3)
        else:
            img, _ = cvzone.putTextRect(img, "WARNING", [250, 350], 10, 10, offset=50, border=5)
    
    
    elif qNo == qTotal:
        img, bbox7 = cvzone.putTextRect(img, "recheck",[50,100],4,2, offset=20, border=5)
        img, bbox8 = cvzone.putTextRect(img, "submit",[50,250],4,2, offset=20, border=5)
        if hands:
            lmList = hands[0]['lmList']
            cursor = lmList[8] #8:食指最上面的點的編號
            length, info = detector.findDistance(lmList[8], lmList[12]) #12:中指
            print(length)
            if length < 30:
                qNo = check(cursor, [bbox7, bbox8], qNo)


    else:    
                
#        score = 0
        a = []
        for mcq in mcqList:
            a.append(mcq.userAns)
#            if mcq.answer == mcq.userAns:
#                score += 1
#        score = round((score / qTotal) * 100, 2)
        img, _ = cvzone.putTextRect(img, "Quiz. Completed", [350, 300], 2, 2, offset=50, border=5)
        img, _ = cvzone.putTextRect(img, f"Your Answer: {a}", [150, 450], 2, 2, offset=50, border=5)
        
                 
    # Draw Progress Bar
    # barValue = 150 + (950 // qTotal) * qNo #(950 = 1150-150)
    # cv2.rectangle(img, (150, 600), (barValue, 650), (0, 255, 0), cv2.FILLED)
    # cv2.rectangle(img, (150, 600), (1100, 650), (255, 0, 255), 5)
    if qNo+1 <= qTotal:
        img, _ = cvzone.putTextRect(img, f'{qNo+1} / {qTotal}', [1130, 635], 2, 2, offset=16)
    
    cv2.imshow("Img",img)
    cv2.waitKey(1)
    if cv2.waitKey(1) == ord("e"):
        break
    
cap.release()
cv2.destroyAllWindows()