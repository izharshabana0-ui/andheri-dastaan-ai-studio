
import streamlit as st
import os, re, json, subprocess, tempfile, textwrap
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import numpy as np

st.set_page_config(page_title="Andheri Dastaan AI Studio", page_icon="👻", layout="centered")

st.markdown("""
<style>
:root { color-scheme: dark; }
.stApp { background: radial-gradient(circle at top, #24152f 0%, #0d0d16 45%, #08080d 100%); color: #f5f1f7; }
.block-container { max-width: 850px; padding-top: 1.2rem; padding-bottom: 3rem; }
h1,h2,h3 { color:#f5eaff !important; }
div[data-testid="stForm"] { border:1px solid #493456; border-radius:16px; padding:16px; }
.stButton>button { width:100%; border-radius:12px; min-height:48px; background:#6d2e83; color:white; border:0; }
.smallnote { color:#b7a9bf; font-size: .88rem; }
</style>
""", unsafe_allow_html=True)

st.title("👻 ANDHERI DASTAAN")
st.caption("Hindi Horror Video Studio · Free-first MVP")
st.info("Yeh pehla working MVP hai: script/scene planning, voiceover aur MP4 assembly. Automatic AI image/video generation abhi connected nahi hai; scene images upload kar sakti hain ya app ke cinematic title-cards use kar sakti hain.")

with st.form("story_form"):
    idea = st.text_area("Apni horror story ka idea likho", placeholder="Jaise: Raat ke 2 baje ek purani train mein ek ladki ko apni hi seat par baitha hua doosra roop dikhta hai...", height=120)
    c1,c2 = st.columns(2)
    with c1:
        ratio = st.selectbox("Video format", ["9:16 Vertical", "16:9 Landscape"])
    with c2:
        duration = st.selectbox("Video duration", ["30 seconds", "60 seconds", "2 minutes", "5 minutes", "7 minutes"])
    tone = st.selectbox("Horror style", ["Cinematic suspense", "Supernatural mystery", "Psychological horror", "Village folklore"])
    make_script = st.form_submit_button("✨ Story aur scenes taiyar karo")

def duration_seconds(v):
    return {"30 seconds":30,"60 seconds":60,"2 minutes":120,"5 minutes":300,"7 minutes":420}[v]

def split_sentences(text):
    chunks = re.split(r'(?<=[।!?])\s+', text.strip())
    return [x.strip() for x in chunks if x.strip()]

def create_outline(idea, seconds, tone):
    seed = idea.strip().rstrip("।.!?")
    count = max(3, min(12, seconds // 10))
    beats = [
        ("HOOK", f"आधी रात को {seed} की शुरुआत एक ऐसी आवाज़ से हुई, जिसे सुनकर सबकी साँसें थम गईं।"),
        ("SETUP", f"शुरुआत में सब कुछ सामान्य लग रहा था, लेकिन {seed} के पीछे छिपा सच कोई नहीं जानता था।"),
        ("SUSPENSE", "अचानक दरवाज़े के बाहर तीन बार दस्तक हुई। कमरे में मौजूद हर शख्स ने एक-दूसरे की तरफ देखा।"),
        ("REVEAL", "आईने में दिखाई देने वाली परछाईं असल में कमरे के अंदर नहीं, उनके ठीक पीछे खड़ी थी।"),
        ("CLIMAX", "उसने पीछे मुड़कर देखा तो वहाँ कोई नहीं था। तभी मोबाइल पर उसी की एक तस्वीर आई—जो अभी-अभी खींची गई थी।"),
        ("ENDING", "सुबह कमरा खाली मिला। दीवार पर सिर्फ एक वाक्य लिखा था—'मैं अभी भी यहीं हूँ।'"),
    ]
    scenes=[]
    for i in range(count):
        label, line = beats[min(i, len(beats)-1)]
        if i >= len(beats):
            line = f"{seed} का रहस्य और गहराता गया। हर अगला कदम उसे उस सच के करीब ले जा रहा था, जिससे वह भागना चाहता था।"
            label = "SUSPENSE"
        scenes.append({"scene":i+1,"beat":label,"narration":line,
                       "visual_prompt":f"cinematic realistic Hindi horror film still, {tone.lower()}, {seed}, atmospheric low-key lighting, detailed environment, clear visible subject, no gore, no text, 16:9 composition"})
    return scenes

if make_script:
    if not idea.strip():
        st.error("Pehle story idea likho.")
    else:
        secs=duration_seconds(duration)
        st.session_state["idea"]=idea
        st.session_state["ratio"]=ratio
        st.session_state["duration"]=secs
        st.session_state["scenes"]=create_outline(idea,secs,tone)
        st.session_state["tone"]=tone

if "scenes" in st.session_state:
    st.divider()
    st.subheader("🎬 Storyboard")
    scenes=st.session_state["scenes"]
    st.write(f"**Format:** {st.session_state['ratio']}  ·  **Duration target:** {st.session_state['duration']} sec")
    for s in scenes:
        with st.expander(f"Scene {s['scene']} · {s['beat']}", expanded=(s['scene']==1)):
            st.write(s["narration"])
            st.caption("Visual prompt")
            st.code(s["visual_prompt"], language="text")
    all_text="\n\n".join([s["narration"] for s in scenes])
    st.download_button("⬇️ Script download karo", all_text, file_name="andheri_dastaan_script.txt")
    st.download_button("⬇️ Scene prompts JSON", json.dumps(scenes,ensure_ascii=False,indent=2), file_name="scene_prompts.json")

    st.divider()
    st.subheader("🖼️ Scene images")
    st.write("Har scene ke liye image upload karo. Agar images nahi hain, app cinematic text-cards banayega.")
    uploads=st.file_uploader("Scene images (order mein select karo)", type=["png","jpg","jpeg"], accept_multiple_files=True)
    st.caption("Tip: 3–8 scene images se shuruaat karo. Uploaded images ko scene order mein use kiya jayega.")

    st.subheader("🎙️ Voiceover")
    st.info("Hindi voiceover abhi is MVP mein connected nahi hai. Is version mein silent MP4 render hota hai; next build mein free Hindi TTS aur audio mixing add karenge.")

    if st.button("🎞️ MP4 video render karo"):
        ffmpeg = subprocess.run(["bash","-lc","command -v ffmpeg"],capture_output=True,text=True).stdout.strip()
        if not ffmpeg:
            st.error("FFmpeg installed nahi mila. Streamlit Cloud par rendering ke liye system package setup chahiye. Local setup README mein diya hai.")
        else:
            with st.spinner("Video render ho raha hai..."):
                work=Path(tempfile.mkdtemp(prefix="andheri_"))
                W,H=(1080,1920) if "9:16" in st.session_state["ratio"] else (1920,1080)
                images=[]
                for idx,s in enumerate(scenes):
                    im=None
                    if uploads and idx < len(uploads):
                        try:
                            im=Image.open(uploads[idx]).convert("RGB")
                        except: im=None
                    if im is None:
                        im=Image.new("RGB",(W,H),(12,10,20))
                        d=ImageDraw.Draw(im)
                        # subtle horizontal bands
                        for y in range(H):
                            shade=int(12+18*y/H)
                            d.line((0,y,W,y),fill=(shade,8,shade+12))
                        title=f"SCENE {idx+1}"
                        body=s["narration"]
                        try:
                            font=ImageFont.truetype("DejaVuSans.ttf", max(24,W//32))
                            small=ImageFont.truetype("DejaVuSans.ttf", max(18,W//48))
                        except:
                            font=ImageFont.load_default(); small=font
                        d.text((W*0.08,H*0.34),title,font=font,fill=(214,170,230))
                        words=body.split(); lines=[]; line=""
                        for word in words:
                            test=(line+" "+word).strip()
                            if d.textbbox((0,0),test,font=small)[2] > W*0.82:
                                lines.append(line); line=word
                            else: line=test
                        if line: lines.append(line)
                        yy=H*0.42
                        for ln in lines:
                            d.text((W*0.08,yy),ln,font=small,fill=(245,238,248)); yy += int(H*0.045)
                    else:
                        im.thumbnail((W,H))
                        canvas=Image.new("RGB",(W,H),(0,0,0))
                        canvas.paste(im,((W-im.width)//2,(H-im.height)//2))
                        im=canvas
                    p=work/f"scene_{idx:03d}.jpg"; im.save(p,quality=90); images.append(p)

                per=max(3, int(st.session_state["duration"]/len(images)))
                concat=work/"list.txt"
                with open(concat,"w") as f:
                    for p in images:
                        f.write(f"file '{p.as_posix()}'\nduration {per}\n")
                    f.write(f"file '{images[-1].as_posix()}'\n")
                out=work/"andheri_dastaan.mp4"
                cmd=["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-vf",f"scale={W}:{H},format=yuv420p","-r","24","-c:v","libx264","-pix_fmt","yuv420p",str(out)]
                result=subprocess.run(cmd,capture_output=True,text=True)
                if result.returncode==0 and out.exists():
                    with open(out,"rb") as f: st.download_button("⬇️ Final MP4 download karo",f.read(),file_name="andheri_dastaan.mp4",mime="video/mp4")
                    st.success("MP4 ready! Yeh version uploaded images ya cinematic text-cards se video banata hai.")
                else:
                    st.error("Rendering fail hua. FFmpeg error:")
                    st.code(result.stderr[-2500:])

st.divider()
st.markdown("**Next upgrade:** free image-generation connector, consistent character reference, Hindi TTS audio mix, background ambience, subtitles, thumbnail aur optional YouTube upload approval.")
st.caption("Privacy: story aur uploaded images isi app session mein process hote hain. Google/YouTube login abhi connected nahi hai.")
