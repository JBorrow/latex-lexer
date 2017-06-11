def run_pandoc(content, bibliography=""):
    if bibliography:
        bib = ["--bibliography={}".format(bibliography)]
    else:
        bib = []

    extra_args = [
        "--mathjax",
        "-F",
        "pandoc-crossref",
        "-F",
        "pandoc-citeproc"] + bib

    print("Running Pandoc (MD -> HTML)")
    OutputData = pypandoc.convert_text(content, "html", format="md", extra_args=extra_args)

    return OutputData

lexer=lex.lex()
lastLecture=0

def process(fileName):
    global lastLecture
    # prepare lexer state
    if lastLecture==0:
        lexer.current={'section':'begining','lecture':'begining'}
    else:
        lexer.current={'section':'begining','lecture':('{0}'.format(lastLecture))}
    lexer.keypoints={}
    lexer.questions={}
    lexer.images={}
    lexer.uids={ 'section':{}, 'lecture':{} , 'keypoint':{}, 'image':{}, 'question':{}}
    lexer.begin={'section':{}, 'lecture':{}}
    lexer.end={'section':{}, 'lecture':{} }
    lexer.sections=[]
    if lastLecture!=0:
        lexer.lectures=["{0}".format(lastLecture)]
    else:
        lexer.lectures=[]
    # parse the tex file

    f=open(tex_dir + fileName,'r')
    txt=f.read()
    lexer.input(txt)
    parser = yacc.yacc()
    result = parser.parse(txt)

    # prepare tex file for conversion to MD
    
    fullTxt=""
    for token in result:
        if token[0]=="TEXT":
            fullTxt+=token[1]
        elif token[0]=='PDFONLY':
            pass   #this is ignored here 
        else:
            fullTxt+="\nMDCOMMENT"+token[2]+"\n"

    # use ltmd to convert
    
    InputText=fullTxt

    # Before we do, remove any random \rules, and \ces

    InputText = re.sub(r"\\rule{.*?}{.*?}",
                        "",
                        InputText)
    #InputText = InputText.replace("\ce", "")

    PreProcessed = ltmd.PreProcess(InputText, ImgPrepend="/")
    Pandocced = ltmd.RunPandoc(PreProcessed.ParsedText, extra=["--mathjax"])
    PostProcessed = ltmd.PostProcess(Pandocced, PreProcessed.ParsedData)
    OutputText = PostProcessed.ParsedText

    # add a last line marker to terminate the opened sections and lectures
    
    fullMD=OutputText.replace('MDCOMMENT',r'[\\] # ')
    endUID=getUID()
    fullMD+=r"[\\] # "+endUID+"\n"
    lexer.end['section'][lexer.current['section']]=endUID
    lexer.end['lecture'][lexer.current['lecture']]=endUID

    # MD --> HTML conversion
    
    fullMDforHTML=re.sub(r"\[\\\\\] # (\d+)", r"<!-- \1 -->", fullMD)
    html=run_pandoc(fullMDforHTML, bibliography=tex_dir + 'bibliography.bib')

    # separate the sections 

    db={'sections':{}}
    seclist=[]
    for sec in lexer.sections:
        regex= r'<!-- {} -->'.format(lexer.begin['section'][sec])
        regex+='(?P<txt>.*?)'
        regex+=r'<!-- {} -->'.format(lexer.end['section'][sec])

        match=re.search(regex ,html,re.MULTILINE+re.DOTALL)
        txt=match.group('txt')
        txt=insertLectureDivs(txt)
        txt+=getKeyPointsHTML(sec)
        txt+=getQuestionsHTML(sec)
        with open(compile_dir + '_'+sec.replace(' ','_')+'.html','w') as of:
            tidy_options = {
                "doctype" : "omit",
                "show-body-only": "yes",           
            }        
            th,errs=tidy.tidy_document(txt, tidy_options)
            of.write(th)
        lecs={}
        if sec in lexer.keypoints.keys():
            for kp in lexer.keypoints[sec]:
                for lec in lexer.keypoints.keys():
                    if lec!=sec :
                        if kp in lexer.keypoints[lec]:
                            if not lec in lecs.keys():
                                lecs[lec]=[]
                            lecs[lec].append(kp)
        if sec in lexer.images.keys():
            images=lexer.images[sec]
        else:
            images=None

        lecnbrs=sorted([int(k) for k in lecs.keys() if not k=='begining' ])
        if lecnbrs:
            lastLecture=lecnbrs[-1]
        leclist=[ {'number':str(i),'kps':lecs[str(i)]} for i in lecnbrs ]
        # treat the case of split lecture
        if 'begining' in lecs.keys():    
            leclist.insert(0,{'number':str(lastLecture),'kps':lecs['begining']})
        if images:
            seclist.append({'lectures':leclist,'name':sec,'image':images[0]})
        else:
            seclist.append({'lectures':leclist,'name':sec})

        if sec in lexer.keypoints.keys():
            items=['\\item {0}'.format(kp) for kp in lexer.keypoints[sec]]
            with open(compile_dir+"/{0}_keypoints.tex".format(sec.replace(' ','-')),'w') as kptex:
                kptex.write("\n".join(items))


            
    leclist=[]
    for lec in lexer.lectures:
        firstSplit,lastSplit=False,False
        if lec==lexer.lectures[0] and lec not in lexer.begin['lecture'].keys():
            # use the first section as the begining of the lecture
            firstSplit=True
            labelBegin=lexer.begin['section'][lexer.sections[0]]
        else:
            labelBegin=lexer.begin['lecture'][lec]
        if lec==lexer.lectures[-1] and lec not in lexer.end['lecture'].keys():
            # use the first section as the begining of the lecture
            lastSplit=True
            labelEnd=lexer.end['section'][lexer.sections[-1]]
        else:
            labelEnd=lexer.end['lecture'][lec]
        regex= r'<!-- {} -->'.format(labelBegin)
        regex+='(?P<txt>.*?)'
        regex+=r'<!-- {} -->'.format(labelEnd)
        # there is no match if this is the lastLecture of the last chapter and
        # there is no content before the first section o this chapter
        match=re.search(regex ,html,re.MULTILINE+re.DOTALL)
        if match:
            txt=getKeyPointsHTML(lec, extra_class=['lecture-kps'])
            txt+=match.group('txt')
            txt+=getQuestionsHTML(lec, extra_class=['lecture-qs'])
            if firstSplit:
                rwaccess='a'
                print ("adding to existing lecture...")
            else:
                rwaccess='w'
            with open(compile_dir + '_Lecture_'+lec+'.html',rwaccess) as of:
                tidy_options = {
                    "doctype" : "omit",
                    "show-body-only": "yes",           
                }        
                th,errs=tidy.tidy_document(txt, tidy_options)
                of.write(th)

            if lec in lexer.images.keys():
                images=lexer.images[lec]
            else:
                images=None


            if images:
                leclist.append({'name':lec,'image':images[0]})
            else:
                leclist.append({'name':lec})


            
    return seclist,leclist


def get_tex(directory):
    if not own_files:
        raw = os.listdir(directory)
        files = []
        for filename in raw:
            if filename[-3:] == 'tex':
                files.append(filename)
            else:
                pass

        return files
    
    return own_files
