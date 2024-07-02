(self.webpackChunk_N_E=self.webpackChunk_N_E||[]).push([[931],{9987:function(e,t,n){Promise.resolve().then(n.bind(n,142))},142:function(e,t,n){"use strict";n.r(t),n.d(t,{default:function(){return eZ}});var r=n(7437),i=n(2197),s=n(1520),o=n(8165),l=n(2265);let a=(0,l.createContext)({isOpen:!1,message:"",severity:"error",duration:null,openPopup:()=>{},closePopup:()=>{}});function c(e){let{children:t}=e,[n,i]=(0,l.useState)(!1),[s,o]=(0,l.useState)(""),[c,d]=(0,l.useState)("error"),[u,x]=(0,l.useState)(null),h=(0,l.useCallback)((e,t,n)=>{i(!0),o(e),t?d(t):d("error"),n&&x(n)},[]),p=(0,l.useCallback)(()=>{i(!1),o(""),d("error")},[]);return(0,r.jsx)(a.Provider,{value:{isOpen:n,message:s,openPopup:h,closePopup:p,severity:c,duration:u},children:t})}let d=()=>l.useContext(a);var u=()=>{let{isOpen:e,closePopup:t,message:n,severity:i}=d();return(0,r.jsx)(s.Z,{open:e,onClose:t,anchorOrigin:{vertical:"top",horizontal:"center"},children:(0,r.jsx)(o.Z,{onClose:t,severity:i,sx:{width:"100%"},elevation:6,children:n})})},x=n(6562),h=n(8866),p=n(7622),m=n(9504),j=n(1733),f=n(9806),v=n(6548),y=n(511),Z=n(659),b=n(1656),g=n(7318),w=n(1326),S=n(8027),C=n(3983),k=n(335),T=n(468),_=n(2834),L=n(7170),W=n(8929),I=n(5911),O=n(9143);function E(e){let{moraTone:{mora:t,tone:n},onChange:i,visible:s=!0,disabled:o=!1}=e;return(0,r.jsxs)(W.Z,{direction:"column",spacing:1,sx:{textAlign:"center",visibility:s?"visible":"hidden"},children:[(0,r.jsx)(y.Z,{children:t}),(0,r.jsxs)(I.Z,{exclusive:!0,color:"primary",orientation:"vertical",value:n,onChange:(e,t)=>{null!==t&&i(t)},disabled:o,children:[(0,r.jsx)(O.Z,{value:1,children:"高"}),(0,r.jsx)(O.Z,{value:0,children:"低"})]})]})}function N(e){let{moraToneList:t,setMoraToneList:n,onChange:i,disabled:s=!1}=e,o=t&&t.length>0?t:[{mora:"ア",tone:0}],l=(e,r)=>{if(i){i(e,r);return}if(!n)return;let s=[...t];s[r]={...s[r],tone:e},n(s)};return(0,r.jsx)(S.Z,{sx:{p:1,mt:2},children:(0,r.jsx)(W.Z,{spacing:1,direction:"row",sx:{maxWidth:"100%",overflow:"auto"},children:o.map((e,n)=>(0,r.jsx)(E,{moraTone:e,onChange:e=>l(e,n),visible:t&&t.length>0,disabled:s},n))})})}var P=()=>{let[e,t]=(0,l.useState)(0),[n,r]=(0,l.useState)(0);return(0,l.useLayoutEffect)(()=>{let e=()=>{t(window.innerWidth),r(window.innerHeight)};return window.addEventListener("resize",e),e(),()=>window.removeEventListener("resize",e)},[]),{width:e,height:n}};async function V(e){let t,n=arguments.length>1&&void 0!==arguments[1]?arguments[1]:{},r=arguments.length>2&&void 0!==arguments[2]?arguments[2]:"json";console.log("fetchApi",e,r,n);let i="".concat("","/api").concat(e),s=await fetch(i,{headers:{"Content-Type":"application/json"},...n});if(!s.ok){let e=await s.json();throw console.error("Error code: ",s.status,"Error message: ",e.detail),Error(e.detail)}switch(r){case"json":t=await s.json();break;case"blob":t=await s.blob();break;case"text":t=await s.text();break;default:t=204===s.status?{}:await s.json()}return console.log("fetchApi result",t),t}var A=n(5253),F=n(6798),R=n(1096),B=n(824),J=n(2184),M=n(1807),z=n(7300),U=n(6917),D=n(7905),G=n(385),q=n(8549),K=n(8409),H=n(1092),Y=n(8038),Q=n(3907),X=n(1052);let $={uuid:"",surface:"",pronunciation:"",moraToneList:[{mora:"ガ",tone:0}],accentIndex:0,priority:5};function ee(e){return{uuid:e.uuid,word:{surface:e.surface,pronunciation:e.pronunciation,accent_type:e.accentIndex===e.moraToneList.length-1?0:e.accentIndex+1,priority:e.priority}}}function et(e){let t=en(e.word);return{uuid:e.uuid,surface:e.word.surface,pronunciation:e.word.pronunciation,moraToneList:t,accentIndex:0===e.word.accent_type?t.length-1:e.word.accent_type-1,priority:e.word.priority}}function en(e){let t=[],n=function(e){let t=RegExp("".concat("[イ][ェ]|[ヴ][ャュョ]|[トド][ゥ]|[テデ][ィャュョ]|[デ][ェ]|[クグ][ヮ]","|").concat("[キシチニヒミリギジビピ][ェャュョ]","|").concat("[ツフヴ][ァ]|[ウスツフヴズ][ィ]|[ウツフヴ][ェォ]","|").concat("[ァ-ヴー]"),"g");return e.match(t)||[]}(e.pronunciation),r=0===e.accent_type?n.length:e.accent_type-1;for(let i=0;i<n.length;i++){let s=n[i],o=0===i&&1===e.accent_type?1:i>0&&i<=r?1:0;t.push({mora:s,tone:o})}return t.push({mora:"ガ",tone:0===e.accent_type?1:0}),t}let er=[{value:0,label:"最低"},{value:3,label:"低"},{value:5,label:"標準"},{value:7,label:"高"},{value:10,label:"最高"}];function ei(e){let{open:t,onClose:n}=e,[i,s]=(0,l.useState)(!0),[o,a]=(0,l.useState)({}),[c,u]=(0,l.useState)($),{surface:x,pronunciation:h,moraToneList:m,accentIndex:j,priority:f}=c,[Z,b]=(0,l.useState)(!1),[S,k]=(0,l.useState)(!1),{openPopup:T}=d();(0,l.useEffect)(()=>{(async()=>{a(await V("/user_dict"))})()},[]);let L=async()=>{b(!1);let e=await V("/normalize",{method:"POST",body:JSON.stringify({text:x})}).catch(e=>(console.error(e),T("正規化に失敗しました","error"),x)),t=(await V("/g2p",{method:"POST",body:JSON.stringify({text:h+"が"})}).catch(e=>(console.error(e),b(!0),[]))).map((e,t)=>({...e,tone:0===t?1:0})),n=t.slice(0,-1).map(e=>e.mora).join("");u({...c,surface:e,moraToneList:t,accentIndex:0,pronunciation:n}),k(!0)},I=e=>{let t=m.map((t,n)=>({...t,tone:0===e?0===n?1:0:0===n?0:n<=e?1:0}));u({...c,accentIndex:e,moraToneList:t})},O=async()=>{if(!x||!h){T("単語と読みを入力してください","error");return}let e=ee(c),t=await V("/user_dict_word",{method:"POST",body:JSON.stringify(e.word)}).catch(e=>{T("登録に失敗しました: ".concat(e),"error")});t&&(T("登録しました","success",3e3),a({...o,[t.uuid]:e.word}),u({...c,uuid:t.uuid}),s(!1))},E=async()=>{if(!x||!h){T("単語と読みを入力してください","error");return}let e=ee(c);await V("/user_dict_word/".concat(e.uuid),{method:"PUT",body:JSON.stringify(e.word)}).catch(e=>{T("更新に失敗しました: ".concat(e),"error")})&&(T("更新しました","success",3e3),a({...o,[e.uuid]:e.word}))},P=async()=>{let e=ee(c);if(!await V("/user_dict_word/".concat(e.uuid),{method:"DELETE"}).catch(e=>{T("削除に失敗しました: ".concat(e),"error")}))return;T("削除しました","success",3e3);let t={...o};delete t[e.uuid],a(t),u($),s(!0)};return(0,r.jsxs)(R.Z,{onClose:n,open:t,fullWidth:!0,maxWidth:"md",children:[(0,r.jsx)(B.Z,{children:"ユーザー辞書"}),(0,r.jsxs)(w.Z,{display:"flex",justifyContent:"space-between",height:600,children:[(0,r.jsxs)(w.Z,{minWidth:200,pb:2,px:2,border:1,borderColor:"divider",borderRadius:1,children:[(0,r.jsx)(J.Z,{children:(0,r.jsx)(M.ZP,{disablePadding:!0,children:(0,r.jsxs)(z.Z,{onClick:()=>{s(!0),u($),k(!1)},selected:i,sx:{justifyContent:"center"},children:[(0,r.jsx)(U.Z,{children:(0,r.jsx)(A.Z,{})}),(0,r.jsx)(D.Z,{primary:"新規登録"})]})})}),(0,r.jsx)(g.Z,{}),(0,r.jsx)(J.Z,{sx:{overflow:"auto",height:"90%"},children:Object.keys(o).map(e=>(0,r.jsx)(M.ZP,{disablePadding:!0,children:(0,r.jsx)(z.Z,{onClick:()=>{console.log(en(o[e])),u(et({uuid:e,word:o[e]})),console.log(et({uuid:e,word:o[e]})),s(!1)},selected:e===c.uuid,children:(0,r.jsx)(D.Z,{primary:o[e].surface})})},e))})]}),(0,r.jsxs)(w.Z,{sx:{flexGrow:1},children:[(0,r.jsxs)(G.Z,{children:[(0,r.jsx)(C.Z,{autoFocus:!0,required:!0,label:"単語（名詞）（自動的に正規化される）",fullWidth:!0,value:x,onChange:e=>u({...c,surface:e.target.value}),sx:{mb:2}}),(0,r.jsxs)(_.Z,{container:!0,spacing:2,justifyContent:"center",alignItems:"center",children:[(0,r.jsx)(_.Z,{xs:9,children:(0,r.jsx)(C.Z,{required:!0,label:"読み（平仮名かカタカナ）",error:Z,helperText:Z?"平仮名かカタカナのみで入力してください":"",fullWidth:!0,value:h,onChange:e=>{u({...c,pronunciation:e.target.value}),k(!1)},sx:{mb:2},onKeyDown:e=>{"Enter"===e.key&&L()}})}),(0,r.jsx)(_.Z,{xs:!0,children:(0,r.jsx)(v.Z,{color:"primary",variant:"outlined",onClick:L,startIcon:(0,r.jsx)(F.Z,{}),sx:{mb:2},fullWidth:!0,children:"情報取得"})})]}),(0,r.jsxs)(W.Z,{children:[(0,r.jsxs)(q.Z,{children:[(0,r.jsx)(K.Z,{children:"アクセント位置（最後に助詞「が」が追加されています）"}),(0,r.jsx)(H.Z,{row:!0,value:j,onChange:e=>I(Number(e.target.value)),sx:{flexWrap:"nowrap",overflow:"auto"},children:m.map((e,t)=>(0,r.jsx)(Y.Z,{value:t,control:(0,r.jsx)(Q.Z,{}),label:e.mora,labelPlacement:"bottom",sx:{mx:0}},t))})]}),(0,r.jsx)(N,{moraToneList:m,disabled:!0}),(0,r.jsx)(y.Z,{sx:{mt:1},children:"優先度"}),(0,r.jsx)(w.Z,{sx:{textAlign:"center"},children:(0,r.jsx)(X.ZP,{value:f,onChange:(e,t)=>{u({...c,priority:t})},marks:er,step:1,min:0,max:10,sx:{mt:2,width:"80%"}})})]})]}),(0,r.jsxs)(W.Z,{direction:"row",spacing:2,justifyContent:"space-around",children:[i&&(0,r.jsx)(v.Z,{type:"submit",variant:"outlined",onClick:O,disabled:!S,children:"登録"}),!i&&(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(v.Z,{type:"submit",variant:"outlined",onClick:E,startIcon:(0,r.jsx)(F.Z,{}),children:"更新"}),(0,r.jsx)(v.Z,{type:"submit",variant:"outlined",onClick:P,startIcon:(0,r.jsx)(p.Z,{}),children:"削除"})]}),(0,r.jsx)(v.Z,{onClick:()=>{n(),u($),k(!1),b(!1),s(!0)},children:"閉じる"})]})]})]})]})}var es=n(1236),eo=n(888),el=n(7351),ea=n(4893);function ec(e){let{value:t,setValue:n,step:i,min:s,max:o,label:l}=e;return(0,r.jsx)(w.Z,{children:(0,r.jsxs)(_.Z,{container:!0,spacing:2,alignItems:"center",justifyContent:"space-between",children:[(0,r.jsxs)(_.Z,{xs:9,children:[(0,r.jsx)(y.Z,{id:"input-slider",gutterBottom:!0,children:l}),(0,r.jsx)(X.ZP,{value:"number"==typeof t?t:s,onChange:(e,t)=>{n(t)},"aria-labelledby":"input-slider",step:i,min:s,max:o})]}),(0,r.jsx)(_.Z,{xs:3,children:(0,r.jsx)(es.Z,{value:t,onChange:e=>{n(""===e.target.value?0:Number(e.target.value))},onBlur:()=>{t<s?n(s):t>o&&n(o)},inputProps:{step:i,min:s,max:o,type:"number"}})})]})})}function ed(e){var t,n,i,s;let{modelList:o,lines:a,setLines:c,currentIndex:d}=e,[u,x]=(0,l.useState)(10),h=e=>{c(a.map((t,n)=>n===d?{...t,...e}:t))},p=e=>{var t;let n=null==o?void 0:o.find(t=>t.name===e);h({model:e,modelFile:(null==n?void 0:n.files[0])||"",style:(null==n?void 0:n.styles[0])||"",speaker:(null==n?void 0:null===(t=n.speakers)||void 0===t?void 0:t[0])||""})};return(0,r.jsxs)(S.Z,{sx:{p:2},children:[(0,r.jsxs)(w.Z,{sx:{display:"flex",justifyContent:"space-between",mb:1,alignItems:"center"},children:[(0,r.jsxs)(y.Z,{children:["テキスト",d+1,"の設定"]}),(0,r.jsx)(eo.Z,{title:"デフォルト設定に戻す",placement:"left",children:(0,r.jsx)(k.Z,{onClick:()=>{var e,t;h({...ej,model:a[d].model,modelFile:a[d].modelFile,text:a[d].text,speaker:a[d].speaker,style:(null===(e=o.find(e=>e.name===a[d].model))||void 0===e?void 0:e.styles.includes("Neutral"))?"Neutral":(null===(t=o.find(e=>e.name===a[d].model))||void 0===t?void 0:t.styles[0])||""})},children:(0,r.jsx)(F.Z,{})})})]}),(0,r.jsxs)(q.Z,{fullWidth:!0,variant:"standard",sx:{mb:1,minWidth:120},children:[(0,r.jsx)(el.Z,{children:"モデル"}),(0,r.jsx)(ea.Z,{value:a[d].model,onChange:e=>p(e.target.value),children:o.map((e,t)=>(0,r.jsx)(b.Z,{value:e.name,children:e.name},t))})]}),(0,r.jsxs)(q.Z,{fullWidth:!0,variant:"standard",sx:{mb:1,minWidth:120},children:[(0,r.jsx)(el.Z,{children:"モデルファイル"}),(0,r.jsx)(ea.Z,{value:a[d].modelFile,onChange:e=>h({modelFile:e.target.value}),children:null===(t=o.find(e=>e.name===a[d].model))||void 0===t?void 0:t.files.map((e,t)=>(0,r.jsx)(b.Z,{value:e,children:e},t))})]}),(0,r.jsxs)(q.Z,{fullWidth:!0,variant:"standard",sx:{mb:1,minWidth:120},children:[(0,r.jsx)(el.Z,{children:"話者"}),(0,r.jsx)(ea.Z,{value:a[d].speaker,onChange:e=>h({speaker:e.target.value}),children:null===(i=o.find(e=>e.name===a[d].model))||void 0===i?void 0:null===(n=i.speakers)||void 0===n?void 0:n.map((e,t)=>(0,r.jsx)(b.Z,{value:e,children:e},t))})]}),(0,r.jsxs)(q.Z,{fullWidth:!0,variant:"standard",sx:{mb:2,minWidth:120},children:[(0,r.jsx)(el.Z,{children:"スタイル"}),(0,r.jsx)(ea.Z,{value:a[d].style,onChange:e=>h({style:e.target.value}),children:null===(s=o.find(e=>e.name===a[d].model))||void 0===s?void 0:s.styles.map((e,t)=>(0,r.jsx)(b.Z,{value:e,children:e},t))})]}),(0,r.jsx)(ec,{label:"スタイルの強さ上限設定",value:u,setValue:e=>x(e),step:.1,min:1,max:20}),(0,r.jsx)(ec,{label:"スタイルの強さ（崩壊したら下げて）",value:a[d].styleWeight,setValue:e=>h({styleWeight:e}),step:.1,min:0,max:u}),(0,r.jsx)(ec,{label:"話速",value:a[d].speed,setValue:e=>h({speed:e}),step:.05,min:.5,max:2}),(0,r.jsx)(ec,{label:"テンポの緩急",value:a[d].sdpRatio,setValue:e=>h({sdpRatio:e}),step:.05,min:0,max:1}),(0,r.jsx)(ec,{label:"Noise",value:a[d].noise,setValue:e=>h({noise:e}),step:.05,min:0,max:1}),(0,r.jsx)(ec,{label:"NoiseW",value:a[d].noisew,setValue:e=>h({noisew:e}),step:.05,min:0,max:1}),(0,r.jsx)(ec,{label:"音高(1以外では音質劣化)",value:a[d].pitchScale,setValue:e=>h({pitchScale:e}),step:.05,min:.7,max:1.3}),(0,r.jsx)(ec,{label:"抑揚(1以外では音質劣化)",value:a[d].intonationScale,setValue:e=>h({intonationScale:e}),step:.05,min:.7,max:1.3}),(0,r.jsx)(ec,{label:"次のテキストとの間の無音",value:a[d].silenceAfter,setValue:e=>h({silenceAfter:e}),step:.05,min:0,max:1.5})]})}var eu=n(4593);function ex(e){let{open:t}=e;return(0,r.jsx)(eu.Z,{sx:{color:"#fff",zIndex:e=>e.zIndex.drawer+1},open:t,children:(0,r.jsx)(T.Z,{color:"inherit"})})}var eh=n(1665),ep=n(8784);function em(e){let{open:t,onClose:n}=e;return(0,r.jsxs)(R.Z,{open:t,fullWidth:!0,maxWidth:"md",children:[(0,r.jsx)(B.Z,{children:"利用規約"}),(0,r.jsxs)(G.Z,{children:[(0,r.jsxs)(y.Z,{children:["Style-Bert-VITS2を利用する際は、",(0,r.jsx)(eh.Z,{href:"https://github.com/litagin02/Style-Bert-VITS2/blob/master/docs/TERMS_OF_USE.md",target:"_blank",rel:"noopener noreferrer",children:"Style-Bert-VITS2の利用規約"}),"を遵守してください。特に、利用するモデルの利用規約がある場合はそれに従わなければなりません。 初期からあるデフォルトモデルの利用規約の抜粋は以下の通りです（完全な利用規約は上記リンクにあります）。"]}),(0,r.jsx)(w.Z,{sx:{fontWeight:"bold"},children:"JVNV"}),(0,r.jsxs)(y.Z,{children:[(0,r.jsx)(eh.Z,{href:"https://huggingface.co/litagin/style_bert_vits2_jvnv",target:"_blank",rel:"noopener noreferrer",children:"「jvnv-」から始まるモデル"}),"は、",(0,r.jsx)(eh.Z,{href:"https://sites.google.com/site/shinnosuketakamichi/research-topics/jvnv_corpus",target:"_blank",rel:"noopener noreferrer",children:"JVNVコーパス"}),"の音声で学習されました。このコーパスのライセンスは",(0,r.jsx)(eh.Z,{href:"https://creativecommons.org/licenses/by-sa/4.0/deed.ja",target:"_blank",rel:"noopener noreferrer",children:"CC BY-SA 4.0"}),"ですので、jvnv-で始まるモデルの利用規約はこれを継承します。"]}),(0,r.jsx)(w.Z,{sx:{fontWeight:"bold"},children:"小春音アミ・あみたろ"}),(0,r.jsxs)(y.Z,{children:["「koharune-ami / amitaro」モデルは、",(0,r.jsx)(eh.Z,{href:"https://amitaro.net/",target:"_blank",rel:"noopener noreferrer",children:"あみたろの声素材工房"}),"のコーパス音声・ライブ配信音声から許可を得て学習されました。利用の際には、",(0,r.jsx)(eh.Z,{href:"https://amitaro.net/voice/voice_rule/",target:"_blank",rel:"noopener noreferrer",children:"あみたろの声素材工房の規約"}),"と",(0,r.jsx)(eh.Z,{href:"https://amitaro.net/voice/livevoice/#index_id6",target:"_blank",rel:"noopener noreferrer",children:"あみたろのライブ配信音声・利用規約"}),"を遵守してください。"]}),(0,r.jsx)(y.Z,{children:"特に、年齢制限がかかりそうなセリフやセンシティブな用途には使用できません。"}),(0,r.jsx)(y.Z,{children:"生成音声を公開する際は（媒体は問わない）、必ず分かりやすい場所に 「あみたろの声素材工房 (https://amitaro.net/)」 の声を元にした音声モデルを使用していることが分かるようなクレジット表記を記載してください： 「Style-BertVITS2モデル: 小春音アミ、あみたろの声素材工房 (https://amitaro.net/)」 「Style-BertVITS2モデル: あみたろ、あみたろの声素材工房 (https://amitaro.net/)」"}),(0,r.jsxs)(y.Z,{children:["完全なモデルの利用規約は",(0,r.jsx)(eh.Z,{href:"https://github.com/litagin02/Style-Bert-VITS2/blob/master/docs/TERMS_OF_USE.md",target:"_blank",rel:"noopener noreferrer",children:"Style-Bert-VITS2の利用規約"}),"をお読みください。"]})]}),(0,r.jsx)(g.Z,{}),(0,r.jsx)(ep.Z,{children:(0,r.jsx)(v.Z,{onClick:n,children:"同意する"})})]})}let ej={text:"",model:"",modelFile:"",style:"",speaker:"",moraToneList:[],accentModified:!1,styleWeight:1,speed:1,sdpRatio:.2,noise:.6,noisew:.8,pitchScale:1,intonationScale:1,silenceAfter:.5};function ef(e){return"string"==typeof e.mora&&(0===e.tone||1===e.tone)}function ev(e){return"string"==typeof e.text&&"string"==typeof e.model&&"string"==typeof e.modelFile&&"string"==typeof e.style&&Array.isArray(e.moraToneList)&&e.moraToneList.every(ef)&&"boolean"==typeof e.accentModified&&"number"==typeof e.styleWeight&&"number"==typeof e.speed&&"number"==typeof e.sdpRatio&&"number"==typeof e.noise&&"number"==typeof e.noisew&&"number"==typeof e.silenceAfter&&"number"==typeof e.pitchScale&&"number"==typeof e.intonationScale}function ey(){let[e,t]=(0,l.useState)([]),[n,i]=(0,l.useState)([ej]),[s,o]=(0,l.useState)(0),{openPopup:a}=d(),[c,u]=(0,l.useState)(""),[W,I]=(0,l.useState)(!1),[O,E]=(0,l.useState)(!1),[A,F]=(0,l.useState)(!1),[R,B]=(0,l.useState)(!0),[J,M]=(0,l.useState)(""),{height:z}=P(),[U,D]=(0,l.useState)(!1),G=()=>D(!0),q=()=>D(!1),K=(0,l.useRef)([]);(0,l.useEffect)(()=>{let e;I(!0);let n=0,r=()=>{V("/models_info").then(e=>{var n;t(e),i([{...ej,model:e[0].name||"",modelFile:e[0].files[0]||"",style:e[0].styles[0]||"",speaker:(null===(n=e[0].speakers)||void 0===n?void 0:n[0])||""}]),I(!1)}).catch(t=>{n<10?(console.log(t),n++,console.log("モデル情報の取得に失敗しました。リトライします。".concat(n,"回目...")),e=setTimeout(r,1e3)):(console.log("モデル情報の取得に失敗しました。リトライ回数: ".concat(n)),console.log(t),a("モデル情報の取得に失敗しました。\n".concat(t),"error"),I(!1))})};return r(),()=>{e&&clearTimeout(e)}},[a]),(0,l.useEffect)(()=>{let e,t=0,n=()=>{V("/version").then(e=>{M(e)}).catch(r=>{t<10?(console.log(r),t++,console.log("バージョン情報の取得に失敗しました。リトライします。".concat(t,"回目...")),e=setTimeout(n,1e3)):(console.log("バージョン情報の取得に失敗しました。リトライ回数: ".concat(t)),console.log(r))})};return n(),()=>{e&&clearTimeout(e)}},[]),(0,l.useEffect)(()=>{console.log("currentLineIndex:",s),K.current[s]&&K.current[s].focus()},[s]);let H=e=>{let t={...n[e],text:"",moraToneList:[],accentModified:!1},r=[...n];r.splice(e+1,0,t),i(r),o(e+1)},Y=e=>{i(n.map((t,n)=>n===s?{...t,...e}:t))},Q=async()=>V("/g2p",{method:"POST",body:JSON.stringify({text:n[s].text})}),X=e=>{Y({text:e,moraToneList:[],accentModified:!1})},$=async()=>{E(!0);let e=n[s].accentModified?n[s].moraToneList:await Q();Y({moraToneList:e});let t={...n[s],moraToneList:e};await V("/synthesis",{method:"POST",body:JSON.stringify(t)},"blob").then(e=>{u(URL.createObjectURL(e))}).catch(e=>{console.error(e),a("音声合成に失敗しました。".concat(e),"error")}).finally(()=>{E(!1)})},ee=async()=>{E(!0);let e=await Promise.all(n.map(async e=>e.accentModified?e.moraToneList:await V("/g2p",{method:"POST",body:JSON.stringify({text:e.text})}))),t=n.map((t,n)=>({...t,moraToneList:e[n]}));i(t),await V("/multi_synthesis",{method:"POST",body:JSON.stringify({lines:t})},"blob").then(e=>{u(URL.createObjectURL(e))}).catch(e=>{console.error(e),a("音声合成に失敗しました。".concat(e),"error")}).finally(()=>{E(!1)})},et=e=>{"Enter"!==e.key||U?"ArrowDown"===e.key?s<n.length-1?o(s+1):H(s):"ArrowUp"===e.key&&s>0&&o(s-1):$()},en=e=>{i([...n.slice(0,e),...n.slice(e+1)]),e<=s&&s>0&&o(s-1)},er=e=>{let t=e.clipboardData.getData("text");if(t){let r=t.split(/[\r\n]+/);r.length>1&&(e.preventDefault(),i([...n.slice(0,s),...r.map((e,t)=>0===t?{...n[s],text:n[s].text+e}:{...n[s],text:e}),...n.slice(s+1)]),o(s+r.length-1))}},[es,eo]=(0,l.useState)(null),el=()=>{eo(null)};return(0,r.jsxs)(r.Fragment,{children:[(0,r.jsx)(j.Z,{position:"static",children:(0,r.jsxs)(f.Z,{children:[(0,r.jsx)(v.Z,{onClick:e=>{eo(e.currentTarget)},color:"inherit",startIcon:(0,r.jsx)(m.Z,{}),children:"メニュー"}),(0,r.jsx)(y.Z,{variant:"h6",sx:{flexGrow:3,textAlign:"center"},children:"Style-Bert-VITS2 エディター"}),(0,r.jsxs)(y.Z,{variant:"subtitle1",children:["SBV2 ver: ",J,", editor ver: ","0.4.1"]}),(0,r.jsxs)(Z.Z,{anchorEl:es,open:!!es,onClose:el,children:[(0,r.jsx)(b.Z,{onClick:()=>{el(),I(!0),V("/models_info").then(e=>{t(e),I(!1)}).catch(e=>{console.error(e),a("モデル情報の取得に失敗しました。\n".concat(e),"error"),I(!1)})},children:"モデル情報をリロード"}),(0,r.jsx)(g.Z,{}),(0,r.jsx)(b.Z,{onClick:()=>{let e=new Blob([JSON.stringify(n)],{type:"application/json"});(0,L.saveAs)(e,"project.json"),el()},children:"プロジェクトの保存"}),(0,r.jsxs)(b.Z,{component:"label",children:["プロジェクトの読み込み",(0,r.jsx)("input",{type:"file",onChange:e=>{var t;el();let n=null===(t=e.target.files)||void 0===t?void 0:t[0];if(!n)return;let r=new FileReader;r.onload=e=>{var t;o(0);let n=null===(t=e.target)||void 0===t?void 0:t.result;if("string"==typeof n)try{let e=JSON.parse(n);if(!Array.isArray(e)||!e.every(ev)){console.error("データがLineState[]型と一致しません。"),a("データが有効な形式ではありません。","error");return}i(e)}catch(e){console.error(e),a("プロジェクトの読み込みに失敗しました。".concat(e),"error")}else console.error("typeof content",typeof n),a("ファイルの読み込みに失敗しました。","error")},r.readAsText(n)},hidden:!0,accept:".json"})]}),(0,r.jsx)(g.Z,{}),(0,r.jsx)(b.Z,{onClick:()=>{F(!0),el()},children:"ユーザー辞書の編集"}),(0,r.jsx)(g.Z,{}),(0,r.jsx)(b.Z,{onClick:()=>{B(!0),el()},children:"利用規約"})]})]})}),(0,r.jsxs)(w.Z,{display:"flex",justifyContent:"space-between",gap:2,mt:2,children:[(0,r.jsxs)(w.Z,{flexGrow:1,width:"100%",overflow:"auto",children:[(0,r.jsx)(S.Z,{sx:{p:2,height:z/2,overflow:"auto"},elevation:2,children:n.map((e,t)=>(0,r.jsxs)(_.Z,{container:!0,spacing:1,mt:2,alignItems:"center",justifyContent:"space-between",sx:{"& .delete-button":{display:"none"},"&:hover .delete-button":{display:"block"},"& .add-line-button":{display:"none"},"&:hover .add-line-button":{display:"block"}},children:[(0,r.jsx)(_.Z,{xs:"auto",children:(0,r.jsx)(h.Z,{fontSize:"small",sx:{display:s===t?"block":"none"}})}),(0,r.jsx)(_.Z,{xs:!0,children:(0,r.jsx)(C.Z,{label:"テキスト".concat(t+1),fullWidth:!0,value:e.text,onFocus:()=>o(t),onChange:e=>X(e.target.value),onKeyDown:et,onCompositionStart:G,onCompositionEnd:q,focused:s===t,onPaste:er,inputRef:e=>K.current[t]=e})}),(0,r.jsx)(_.Z,{xs:"auto",children:(0,r.jsx)(k.Z,{className:"delete-button",disabled:1===n.length,onClick:()=>en(t),title:"この行を削除する",children:(0,r.jsx)(p.Z,{})})}),(0,r.jsx)(_.Z,{xs:"auto",children:(0,r.jsx)(k.Z,{className:"add-line-button",onClick:()=>H(t),title:"行を追加する",children:(0,r.jsx)(x.Z,{})})})]},t))}),(0,r.jsx)(N,{moraToneList:n[s].moraToneList,setMoraToneList:e=>Y({moraToneList:e,accentModified:!0})}),(0,r.jsxs)(w.Z,{mt:2,sx:{position:"relative",display:"flex",justifyContent:"center",alignItems:"center"},children:[(0,r.jsx)(v.Z,{variant:"contained",color:"primary",disabled:O,onClick:$,children:"音声合成"}),O&&(0,r.jsx)(T.Z,{size:24,sx:{position:"absolute"}})]}),(0,r.jsxs)(w.Z,{mt:2,sx:{position:"relative",display:"flex",justifyContent:"center",alignItems:"center"},children:[(0,r.jsx)(v.Z,{variant:"outlined",color:"primary",disabled:O,onClick:ee,children:"全てのテキストを音声合成"}),O&&(0,r.jsx)(T.Z,{size:24,sx:{position:"absolute"}})]}),c&&(0,r.jsx)("audio",{src:c,controls:!0,autoPlay:!0})]}),(0,r.jsx)(w.Z,{width:"30%",maxWidth:350,minWidth:200,children:(0,r.jsx)(ed,{modelList:e,lines:n,currentIndex:s,setLines:i})})]}),(0,r.jsx)(ex,{open:W}),(0,r.jsx)(ei,{open:A,onClose:()=>F(!1)}),(0,r.jsx)(em,{open:R,onClose:()=>B(!1)})]})}function eZ(){return(0,r.jsx)(i.Z,{maxWidth:"xl",children:(0,r.jsxs)(c,{children:[(0,r.jsx)(u,{}),(0,r.jsx)(ey,{})]})})}}},function(e){e.O(0,[154,257,971,23,744],function(){return e(e.s=9987)}),_N_E=e.O()}]);