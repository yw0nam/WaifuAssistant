

# **An Architectural Analysis of Live2D Implementations in Open-Source AI VTuber Projects**

### **Section 1: Introduction to AI VTuber Architectures**

#### **1.1. The Open-Source AI VTuber Landscape**

The emergence of AI-driven virtual YouTubers (VTubers), popularized by projects like Neuro-sama, has inspired a vibrant open-source movement dedicated to creating interactive, artificially intelligent digital personas.1 The central technical challenge in this domain is the seamless integration of a Large Language Model (LLM) with a real-time graphics rendering system. This involves translating abstract AI outputs—text, emotional states, and synthesized speech—into the concrete, expressive animations of a 2D character, thereby creating the illusion of a sentient, interactive being. Developers venturing into this space are faced with a series of architectural decisions that profoundly impact the project's complexity, capabilities, and platform compatibility.

#### **1.2. The Two Dominant Architectural Paradigms**

Analysis of the leading open-source AI VTuber repositories reveals a clear bifurcation in implementation strategy. This fundamental architectural fork dictates the technology stack, development workflow, and the final user experience. Developers must choose between offloading rendering responsibilities to a specialized application or building a comprehensive, full-stack solution.

Paradigm 1: VTube Studio (VTS) API Offloading  
This approach is backend-centric, treating the popular VTube Studio application as a dedicated rendering service. A primary application, typically written in Python, orchestrates the AI logic—processing speech-to-text (STT), querying the LLM, and generating text-to-speech (TTS) audio. It then communicates with a running instance of VTube Studio via its public API to control the avatar. In this model, VTS handles the computationally intensive tasks of rendering the Live2D model, applying physics, blending animations, and performing lip-sync, effectively acting as a remote-controlled animation engine.1  
Paradigm 2: Direct Frontend Rendering  
This approach represents a full-stack development model, comprising a distinct backend for AI logic and a custom frontend for rendering. The backend serves the AI components, while the frontend, typically a web application or a desktop client built with technologies like Electron, is responsible for rendering the Live2D model directly. This is achieved using graphics libraries that leverage WebGL. This paradigm grants the developer complete control over the entire pipeline but also assigns full responsibility for implementing rendering loops, animation logic, user interaction, and lip-synchronization mechanisms.3

#### **1.3. Repository Overview**

The five repositories examined in this report each adopt one of these two paradigms, serving as excellent case studies for their respective architectural choices. Their core technologies and community traction provide a snapshot of the current landscape.

**Table 1: High-Level Repository Overview**

| Repository | Primary Approach | Core Technology Stack (Languages) | GitHub Stars |
| :---- | :---- | :---- | :---- |
| kimjammer/Neuro | VTS Offloading | Python | 759 1 |
| moeru-ai/airi | Direct Frontend Rendering | TypeScript, Vue, Rust | 619 3 |
| jofizcd/Soul-of-Waifu | VTS Offloading (Inferred) | Python | 278 9 |
| Open-LLM-VTuber/Open-LLM-VTuber | Direct Frontend Rendering | Python, TypeScript, React | 3,600 2 |
| SugarcaneDefender/z-waif | VTS Offloading | Python | 295 5 |

---

### **Section 2: The VTube Studio Offloading Paradigm**

This paradigm leverages the robust and feature-rich VTube Studio application as a black-box renderer, allowing developers to focus primarily on the AI and logic components of their VTuber. The core of this approach is interfacing with the VTS API to remotely control the avatar.

#### **2.1. Architectural Principles and Core Mechanisms**

The VTS Offloading model is built upon a few key mechanisms that simplify the development process significantly.

* **The VTS API as a Control Plane:** VTube Studio exposes an extensive API that operates over a WebSocket connection. This allows external plugins and scripts to send JSON-formatted requests to control nearly every aspect of the application. The official VTS API documentation details a wide range of capabilities, including triggering hotkeys, setting Live2D parameter values directly, loading models, manipulating scene items, and receiving event notifications.12 This API is the fundamental bridge between the developer's AI logic and the visual representation of the character.  
* **Lip-Sync via Virtual Audio Cable:** A crucial technique employed by this paradigm is the offloading of lip-sync. Instead of performing complex audio analysis to map phonemes or visemes to mouth shapes, the developer's application simply routes the audio output from its TTS engine to a virtual audio device (e.g., VB-CABLE). VTube Studio is then configured to use this virtual device as its microphone input. VTS's built-in functionality links microphone volume to the ParamMouthOpen parameter of the Live2D model, creating effective and automatic lip-sync without any audio processing code in the AI application itself. This is explicitly the method used by the Neuro project.1  
* **Animation & Expression via Hotkeys:** The most common method for controlling the avatar's expressions (e.g., happy, sad, angry) and triggering pre-made animations is through VTS hotkeys. The developer first configures these hotkeys within the VTS interface, linking them to specific expressions or animations. The AI backend then parses the LLM's output for emotional cues and sends an API request to trigger the corresponding hotkey by its unique ID.

#### **2.2. Case Study: SugarcaneDefender/z-waif**

The z-waif project is a quintessential example of the VTS Offloading paradigm. It functions as a Python-based hub that integrates various local AI services (like Oobabooga for the LLM, RVC for voice conversion, and Whisper for STT) and uses VTS for the visual front end.5

* **VTS API Integration:** The project's requirements.txt file explicitly lists pyvts==0.3.3 as a dependency.14  
  pyvts is a popular Python library designed to simplify interaction with the VTS API. Based on the library's documentation, the implementation pattern within z-waif likely involves the following asynchronous steps 15:  
  1. An instance of the pyvts.vts() class is created.  
  2. An asyncio-powered WebSocket connection is established with VTS using await vts.connect().  
  3. The plugin authenticates with VTS via await vts.request\_authenticate().  
  4. When the LLM determines an emotion should be displayed, a request to trigger the associated hotkey is sent, for example, await vts.vts\_request.requestTriggerHotkey("MyHappyExpressionHotkey").  
* **Control Flow:** The primary script, main.py 11, orchestrates the entire interaction loop. User speech is transcribed (STT), sent to the LLM for a response, and the response text is converted back to speech (TTS). The generated audio from the TTS engine is played through a virtual audio cable to drive the model's lip-sync in VTS. Simultaneously, the LLM's text response is parsed for emotional markers, which are used to trigger the appropriate VTS hotkeys via the  
  pyvts library.

#### **2.3. Case Study: kimjammer/Neuro**

The Neuro project, a recreation of Neuro-sama, also follows the VTS Offloading paradigm with a Python backend.1 However, it presents a notable variation in its implementation.

* **VTS API Integration:** Unlike z-waif, the Neuro project's dependencies do not include pyvts or any other known VTS API library.1 Furthermore, the repository's activity log includes a commit message "Update Vtube Studio connection code".18 This strongly suggests that the project employs a custom, lightweight WebSocket implementation to communicate with the VTS API directly, rather than relying on a third-party library. This choice offers greater control and fewer dependencies at the cost of reimplementing the API communication logic.  
* **Frontend-Driven Control:** The Neuro architecture introduces a web-based frontend that serves as a control panel. The README states, "You can also trigger hotkeys or preprogrammed animations... from the frontend".1 The presence of a  
  socketioServer.py file 1 indicates that this frontend communicates with the Python backend via Socket.IO. The backend then acts as a bridge, relaying commands received from the web UI to the VTS API.

#### **2.4. Case Study: jofizcd/Soul-of-Waifu**

The Soul-of-Waifu project is focused heavily on the AI backend, providing extensive support for various LLM and TTS services, including local models.9

* **Architectural Assessment:** The project is written almost entirely in Python (99.9%) and lacks a separate frontend repository or any web rendering code.9 Its feature list, however, explicitly mentions the ability to "take a look at your character by integrating an animated Live2D model".9 This combination of a Python-only stack and a Live2D animation feature makes the VTS Offloading paradigm the only logical conclusion for its implementation.  
* **Likely Implementation:** It is highly probable that Soul-of-Waifu uses a Python library such as pyvts 15 or the newer  
  PyTubeStudio 19 to connect to a running VTS instance. The application would parse the LLM's output for emotional context and trigger corresponding hotkeys to change the avatar's expressions, following a similar pattern to  
  z-waif.

#### **2.5. Paradigm Analysis: Strengths and Weaknesses**

The VTube Studio Offloading paradigm offers a distinct set of trade-offs for developers.

* **Strengths:**  
  * **Rapid Development:** By abstracting away the complexities of rendering, physics, and animation, developers can build a functional AI VTuber prototype very quickly.  
  * **High-Quality Rendering:** Projects benefit from VTS's mature and highly optimized rendering engine, which includes advanced features like lighting, item tracking, and smooth physics, all out-of-the-box.  
  * **Simplified Lip-Sync:** The virtual audio cable method is exceptionally simple to implement and yields very effective results.  
* **Weaknesses:**  
  * **Platform Dependency:** The approach is fundamentally tied to the platforms that VTube Studio supports, primarily Windows and macOS. Native Linux support can be problematic.20  
  * **External Software Requirement:** The end-user experience is more complex, as it requires the user to install, configure, and run VTube Studio alongside the AI application.  
  * **Limited Customization:** Developers are constrained by the features exposed through the VTS API. Deep customization of the rendering process or the creation of novel interaction mechanics not supported by the API is impossible.

---

### **Section 3: The Direct Frontend Rendering Paradigm**

This paradigm represents a more ambitious, full-stack approach to creating an AI VTuber. It involves building a complete client-server application, giving the developer end-to-end control over the user experience at the cost of significantly increased complexity.

#### **3.1. Architectural Principles and Core Mechanisms**

This model is defined by its separation of concerns between a backend for logic and a frontend for presentation.

* **Client-Server Model:** The architecture consists of a backend server, usually written in Python, responsible for all AI-related tasks (LLM, STT, TTS). This backend communicates with a frontend client, which can be a web page or a standalone desktop application built with a framework like Electron. The frontend's sole purpose is to render the Live2D avatar and handle user input.  
* **WebSocket for Real-Time State Sync:** A persistent, low-latency WebSocket connection is the lifeline between the backend and frontend. The backend pushes a continuous stream of state updates to the frontend as JSON messages. These messages contain all the information needed to animate the avatar, such as which expression to display, which motion to play, and the current value for lip-sync parameters.  
* **Frontend Rendering with WebGL:** The frontend application uses a JavaScript or TypeScript library that leverages the browser's WebGL API to render the Live2D model. This library handles the parsing of model files (.moc3, .model3.json), textures, and physics data, and draws the animated character onto an HTML canvas element.  
* **The Lip-Sync Challenge:** This paradigm shifts the burden of lip-sync entirely to the developer. Since there is no VTube Studio to listen to a virtual microphone, the system must generate lip movement data programmatically. The existence of specialized libraries like pixi-live2d-display-lipsyncpatch 21 highlights that this is a non-trivial problem. The typical implementation involves the backend analyzing the generated TTS audio to extract amplitude information. This data (e.g., a normalized value from 0.0 to 1.0) is then sent over the WebSocket to the frontend, which uses the rendering library's API to map this value directly to the Live2D model's  
  ParamMouthOpen parameter on each frame.

#### **3.2. Case Study: Open-LLM-VTuber**

Open-LLM-VTuber is the most prominent example of the Direct Frontend Rendering paradigm, featuring a well-defined separation between its Python backend and its TypeScript/React frontend.2

* **System Architecture:** The project is split into two main repositories: Open-LLM-VTuber for the Python backend and Open-LLM-VTuber-Web for the frontend, which can be run in a browser or as an Electron desktop app.6 This modular design facilitates parallel development and clear separation of concerns.  
* **The Rendering Pipeline with pixi-live2d-display:** The frontend heavily relies on the pixi-live2d-display library, a popular wrapper for rendering Live2D models within the PixiJS WebGL engine.  
  * **Model Loading:** As described in the library's documentation 22 and confirmed by the project's own character customization guide 24, models are loaded asynchronously from their configuration files:  
    const model \= await Live2DModel.from('path/to/your/model.model3.json');. Model assets are placed in the live2d-models directory 2 and registered in a central  
    model\_dict.json file.  
  * **Rendering Loop:** The library integrates with the PIXI.Ticker to establish an animation loop, which continuously redraws the model and updates its parameters on each frame, ensuring smooth animation.22  
* **Backend-Frontend Interface:** The Python backend, specifically server.py 25, initiates a WebSocket server. The frontend client connects to this server to receive commands. A key feature is the ability to "set emotion mapping to control model expressions from the backend".2  
* **Implementation of Emotion & Interaction:** The system for controlling expressions is elegant and powerful. The model\_dict.json file defines an emotionMap that links simple keywords (e.g., "joy", "anger") to specific expression files (e.g., "f01", "f03") defined within the Live2D model's data.24 The LLM is prompted to include these keywords in its response, formatted as tags (e.g.,  
  \[joy\] I'm so happy to see you\!). The Python backend parses this tag, removes it from the text to be spoken, and sends a concise JSON message like {"emotion": "joy"} over the WebSocket. The frontend receives this message and uses the pixi-live2d-display API to activate the corresponding expression on the model. User interactions like clicks are handled entirely on the frontend, which uses the library's hit-testing capabilities to trigger tapMotions also defined in model\_dict.json.24

#### **3.3. Case Study: moeru-ai/airi**

The airi project takes a "web-first" approach, architected as a monorepo using Vue, TypeScript, and some Rust components for performance-critical tasks.3 It aims to leverage the latest browser technologies, including WebGPU, WebAssembly, and Web Workers, to create a highly optimized, browser-native experience.3

* **The Rendering Pipeline:** airi's implementation demonstrates a deep, bespoke integration with its toolchain. The associated @proj-airi GitHub organization contains a repository named unplugin-live2d-sdk.26 An  
  unplugin is a build-time tool for modern JavaScript bundlers like Vite and Webpack. The creation of a custom plugin specifically for the Live2D SDK indicates a highly tailored integration designed to optimize how Live2D assets are imported and bundled within their Vue/Vite ecosystem. This goes beyond simply using a rendering library off-the-shelf and involves building the surrounding toolchain for maximum efficiency.  
* **Implementation Details:** The project's commit history and release notes confirm that the rendering logic is encapsulated within their Vue components. Features like "feat(stage-ui): animate idle eye and focus movements on Live2D models" and "feat(stage-web): load and save live2d model" are directly implemented in the UI packages.8 The relevant code can be found in the  
  packages/stage-ui and apps/stage-web directories, where Vue components manage the Live2D canvas and its state.3

#### **3.4. Paradigm Analysis: Strengths and Weaknesses**

The Direct Frontend Rendering paradigm offers ultimate flexibility but requires significant engineering effort.

* **Strengths:**  
  * **Full Control & Customization:** The developer controls every aspect of the rendering pipeline, allowing for unique features and deep integration with the application's UI.  
  * **Cross-Platform Native:** A web-based frontend is inherently cross-platform. By wrapping it in Electron, a consistent desktop application can be distributed for Windows, macOS, and Linux without modification.  
  * **No External Dependencies:** The end-user experience is streamlined. The application is self-contained and does not require the installation or configuration of any other software like VTube Studio.  
* **Weaknesses:**  
  * **High Implementation Complexity:** The developer is responsible for everything: model loading, the render loop, state management, lip-sync, physics simulation, and interaction logic. This is a substantial undertaking.  
  * **Performance Considerations:** Achieving smooth, high-framerate rendering, especially with complex models or on devices with less powerful GPUs, is a significant engineering challenge that requires careful optimization.  
  * **Reinventing the Wheel:** Many features that are standard in VTube Studio, such as its advanced physics engine, item system, and scene management, must be built from scratch if desired.

---

### **Section 4: Comparative Analysis and Developer's Guide**

This section synthesizes the analysis into a practical guide, providing a direct comparison of the projects and a framework to help developers choose the right approach for their goals.

#### **4.1. Feature and Technology Matrix**

The following table provides a detailed, at-a-glance comparison of the Live2D implementation in each repository, serving as a core reference for technical decision-making.

**Table 2: Detailed Live2D Implementation Matrix**

| Repository | Live2D Method | Key Library/API | Lip-Sync Method | Expression Control | Frontend Tech | Backend Tech | Platform Support |
| :---- | :---- | :---- | :---- | :---- | :---- | :---- | :---- |
| Neuro | VTS Offloading | Custom WebSocket | Virtual Audio Cable | VTS Hotkeys | Web (Control Panel) | Python | Win/macOS |
| airi | Direct Rendering | Custom (unplugin-live2d-sdk) | Backend-driven | WebSocket State Sync | Vue, Electron | TypeScript, Rust | Web, All Desktop |
| Soul-of-Waifu | VTS Offloading | Inferred (pyvts or similar) | Virtual Audio Cable | VTS Hotkeys | N/A | Python | Win/macOS |
| Open-LLM-VTuber | Direct Rendering | pixi-live2d-display | Backend-driven | WebSocket State Sync | React, Electron | Python | Web, All Desktop |
| z-waif | VTS Offloading | pyvts | Virtual Audio Cable | VTS Hotkeys | N/A | Python | Win/macOS/Linux |

#### **4.2. The Developer's Decision Framework**

Choosing the right architectural path depends entirely on the project's goals, the developer's skillset, and the desired user experience.

* **Scenario 1: "I want to build a quick prototype on Windows/macOS and focus on the AI."**  
  * **Recommendation:** Use the **VTS Offloading** paradigm. This approach minimizes frontend development work and allows for rapid iteration on the core AI logic.  
  * **Path:** Follow the model of SugarcaneDefender/z-waif.5 A Python backend using the  
    pyvts library 14 provides a well-documented and direct path to controlling VTube Studio. The "virtual audio cable" method for lip-sync is simple and effective.  
* **Scenario 2: "I want to build a cross-platform desktop pet with maximum customizability and no external dependencies."**  
  * **Recommendation:** Use the **Direct Frontend Rendering** paradigm. This gives you full control over the application's appearance and behavior and provides a self-contained executable for end-users.  
  * **Path:** The architecture of Open-LLM-VTuber is the ideal blueprint.2 A Python backend for AI processing coupled with a React/Electron frontend is a powerful and popular combination. The  
    pixi-live2d-display library 21 is the proven and well-supported choice for rendering. Be prepared to design a robust WebSocket protocol to manage state synchronization between the backend and frontend.  
* **Scenario 3: "I am a web developer and want to build a browser-native experience using the latest web technologies."**  
  * **Recommendation:** Use the **Direct Frontend Rendering** paradigm, with a web-first focus.  
  * **Path:** The moeru-ai/airi project serves as an excellent source of inspiration.3 This path favors developers with strong frontend skills in modern frameworks like Vue or Svelte. It offers the potential for high performance and cutting-edge features by leveraging technologies like WebGPU and WebAssembly, but it may also involve working with a less mature or less documented technology stack.

#### **4.3. Reusable Implementation Patterns**

The following code patterns illustrate the core mechanics of each paradigm.

* Pattern 1: Establishing a VTS Connection with pyvts (Python)  
  This pattern shows the basic asyncio structure for connecting to VTS and triggering a hotkey.  
  Python  
  import asyncio  
  import pyvts

  async def main():  
      plugin\_info \= {  
          "plugin\_name": "MyAIPlugin",  
          "developer": "MyName"  
      }  
      vts \= pyvts.vts(plugin\_info=plugin\_info)

      try:  
          await vts.connect()  
          await vts.request\_authenticate() \# Handles token request and authentication

          \# Example: Trigger a hotkey named "HappyEmote"  
          hotkey\_data \= await vts.request(vts.vts\_request.requestHotkeysInCurrentModel())  
          for hotkey in hotkey\_data\['data'\]\['availableHotkeys'\]:  
              if hotkey\['name'\] \== 'HappyEmote':  
                  await vts.request(vts.vts\_request.requestTriggerHotkey(hotkey))  
                  print("Triggered 'HappyEmote' hotkey.")  
                  break  
      finally:  
          await vts.close()

  if \_\_name\_\_ \== "\_\_main\_\_":  
      asyncio.run(main())

* Pattern 2: Loading a Live2D Model with pixi-live2d-display (TypeScript)  
  This pattern demonstrates how to load a model and add it to a PixiJS stage.  
  TypeScript  
  import \* as PIXI from 'pixi.js';  
  import { Live2DModel } from 'pixi-live2d-display';

  // Expose PIXI to the window for the library's Ticker to work automatically  
  window.PIXI \= PIXI;

  (async function() {  
      const app \= new PIXI.Application({  
          view: document.getElementById('canvas') as HTMLCanvasElement,  
          autoStart: true,  
          resizeTo: window,  
      });

      const modelUrl \= '/path/to/your/model.model3.json';  
      const model \= await Live2DModel.from(modelUrl);

      app.stage.addChild(model);  
      model.scale.set(0.4);  
  })();

* Pattern 3: Structuring WebSocket Messages for State Control  
  This pattern shows example JSON payloads sent from a backend to a frontend to control the avatar.  
  JSON  
  // Message to change the model's expression  
  {  
    "type": "expression",  
    "name": "joy"   
  }

  // Message to update the lip-sync value (e.g., based on audio amplitude)  
  {  
    "type": "lipsync",  
    "value": 0.75   
  }

  // Message to play a specific motion  
  {  
    "type": "motion",  
    "group": "TapBody",  
    "index": 1  
  }

* Pattern 4: Mapping Audio to Mouth Parameters (Frontend Pseudo-code)  
  This conceptual pattern shows how a frontend might process a lipsync message.  
  JavaScript  
  // Assume 'model' is a loaded Live2DModel instance  
  // and 'websocket' is an active WebSocket connection

  websocket.onmessage \= (event) \=\> {  
      const data \= JSON.parse(event.data);

      if (data.type \=== 'lipsync') {  
          // The Live2D parameter for mouth opening is often 'ParamMouthOpenY'  
          // The value is typically between 0 (closed) and 1 (open)  
          model.internalModel.coreModel.setParameterValueById('ParamMouthOpenY', data.value);  
      }  
  };

---

### **Section 5: Conclusion and Future Outlook**

The open-source AI VTuber ecosystem is rapidly evolving, driven by two distinct but effective architectural philosophies. The choice between them represents a fundamental trade-off between development speed and ultimate control.

#### **5.1. Summary of Architectural Trade-offs**

The analysis presents a clear dichotomy for developers. The **VTube Studio Offloading** paradigm offers unparalleled development speed, access to a rich set of pre-built rendering features, and a simplified approach to complex problems like lip-sync. However, this convenience comes at the cost of a hard dependency on external software, platform limitations, and a ceiling on customization defined by the VTS API.

Conversely, the **Direct Frontend Rendering** paradigm provides complete control, true cross-platform portability, and a self-contained user experience. This power and flexibility demand a significantly higher investment in engineering effort, requiring developers to tackle the challenges of rendering performance, state synchronization, and the implementation of all avatar-related features from the ground up.

#### **5.2. Emerging Trends and Future Directions**

Several trends are poised to shape the future of this field:

* **The Cubism 5 SDK:** Most current open-source rendering tools, such as pixi-live2d-display, primarily support Live2D Cubism versions up to 4\.24 The adoption of the newer Cubism 5 SDK, which offers new creative features like blend shape masks and improved physics, will necessitate significant updates to these core rendering libraries. Projects that successfully integrate Cubism 5 will gain access to more expressive and dynamic avatars.  
* **The Rise of WebGPU:** The airi project's early adoption of WebGPU is a forward-looking choice.3 As WebGPU achieves ubiquitous browser support, it promises to deliver lower-level access to GPU hardware and superior performance compared to WebGL. This could enable more complex models, higher-resolution textures, and more sophisticated visual effects to run smoothly directly in the browser, further blurring the line between web and native applications.  
* **Advanced AI-Avatar Integration:** The next frontier lies in creating a deeper, more nuanced connection between the AI's cognitive state and the avatar's expression. Projects are already planning for features like "internal dialoguing for chain of thought / reasoning" and "emotional / tone understanding".5 This suggests a future beyond simple keyword-based emotion mapping. Instead, the AI's internal reasoning process—its uncertainty, its consideration of multiple responses, its shifts in tone—could be visualized through subtle, continuous changes in the avatar's facial expression, posture, and breathing. This will require more granular and higher-bandwidth state synchronization protocols between the AI and the rendering engine.

#### **5.3. Final Recommendations**

For developers entering this space, the optimal path is dictated by project goals and available expertise.

* The choice of architecture should be a deliberate one. For those focused on innovating in AI behavior, dialogue systems, or memory, the VTS Offloading paradigm is the most efficient starting point. It allows for the validation of core AI concepts without the significant overhead of building a custom rendering engine.  
* For projects where a unique user experience, deep UI integration, or a self-contained, cross-platform application is paramount, the Direct Frontend Rendering paradigm is necessary. Developers choosing this path should budget significant time for frontend engineering and performance optimization.  
* Finally, the continued growth and sophistication of these projects depend on community collaboration. Contributing to these open-source repositories—whether by improving documentation, fixing bugs, or implementing new features—is the most effective way to help push the entire ecosystem forward and make the creation of compelling AI companions accessible to all.

#### **참고 자료**

1. kimjammer/Neuro: A recreation of Neuro-Sama originally created in 7 days. \- GitHub, 6월 24, 2025에 액세스, [https://github.com/kimjammer/Neuro](https://github.com/kimjammer/Neuro)  
2. Open-LLM-VTuber/Open-LLM-VTuber: Talk to any LLM with hands-free voice interaction, voice interruption, and Live2D taking face running locally across platforms \- GitHub, 6월 24, 2025에 액세스, [https://github.com/Open-LLM-VTuber/Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)  
3. moeru-ai/airi: A container of souls of AI waifu / virtual characters to bring them into our worlds, wishing to achieve Neuro-sama's altitude, completely LLM and AI driven, capable of realtime voice chat, Minecraft playing, Factorio playing. Can be run in Browser or Desktop. \- GitHub, 6월 24, 2025에 액세스, [https://github.com/moeru-ai/airi](https://github.com/moeru-ai/airi)  
4. So... you wanna get started creating your own Neuro? : r/NeuroSama \- Reddit, 6월 24, 2025에 액세스, [https://www.reddit.com/r/NeuroSama/comments/1jtte9s/so\_you\_wanna\_get\_started\_creating\_your\_own\_neuro/](https://www.reddit.com/r/NeuroSama/comments/1jtte9s/so_you_wanna_get_started_creating_your_own_neuro/)  
5. z-waif/README.md at main \- GitHub, 6월 24, 2025에 액세스, [https://github.com/SugarcaneDefender/z-waif/blob/main/README.md](https://github.com/SugarcaneDefender/z-waif/blob/main/README.md)  
6. Open-LLM-VTuber \- GitHub, 6월 24, 2025에 액세스, [https://github.com/Open-LLM-VTuber](https://github.com/Open-LLM-VTuber)  
7. kimjammer \- GitHub, 6월 24, 2025에 액세스, [https://github.com/kimjammer](https://github.com/kimjammer)  
8. Releases · moeru-ai/airi \- GitHub, 6월 24, 2025에 액세스, [https://github.com/moeru-ai/airi/releases](https://github.com/moeru-ai/airi/releases)  
9. Discover the world of artificial intelligence and interact with your favorite characters without needing to learn tons of information. Bring your Waifu to life with Soul of Waifu\! \- GitHub, 6월 24, 2025에 액세스, [https://github.com/jofizcd/Soul-of-Waifu](https://github.com/jofizcd/Soul-of-Waifu)  
10. Releases · jofizcd/Soul-of-Waifu \- GitHub, 6월 24, 2025에 액세스, [https://github.com/jofizcd/Soul-of-Waifu/releases](https://github.com/jofizcd/Soul-of-Waifu/releases)  
11. SugarcaneDefender/z-waif: Fully local program to make ... \- GitHub, 6월 24, 2025에 액세스, [https://github.com/SugarcaneDefender/z-waif](https://github.com/SugarcaneDefender/z-waif)  
12. DenchiSoft/VTubeStudio: VTube Studio API Development Page \- GitHub, 6월 24, 2025에 액세스, [https://github.com/DenchiSoft/VTubeStudio](https://github.com/DenchiSoft/VTubeStudio)  
13. VTubeStudio/README.md at master \- GitHub, 6월 24, 2025에 액세스, [https://github.com/DenchiSoft/VTubeStudio/blob/master/README.md](https://github.com/DenchiSoft/VTubeStudio/blob/master/README.md)  
14. requirements.txt \- SugarcaneDefender/z-waif · GitHub, 6월 24, 2025에 액세스, [https://github.com/SugarcaneDefender/z-waif/blob/main/requirements.txt](https://github.com/SugarcaneDefender/z-waif/blob/main/requirements.txt)  
15. Welcome to pyvts \! — pyvts 0.3.3 documentation, 6월 24, 2025에 액세스, [https://genteki.github.io/pyvts/](https://genteki.github.io/pyvts/)  
16. Tutorial — pyvts 0.3.3 documentation, 6월 24, 2025에 액세스, [https://genteki.github.io/pyvts/toctree2\_tutorial.html](https://genteki.github.io/pyvts/toctree2_tutorial.html)  
17. Genteki/pyvts: A python library for interacting with the VTube Studio API \- GitHub, 6월 24, 2025에 액세스, [https://github.com/Genteki/pyvts](https://github.com/Genteki/pyvts)  
18. Activity · kimjammer/Neuro · GitHub, 6월 24, 2025에 액세스, [https://github.com/kimjammer/Neuro/activity](https://github.com/kimjammer/Neuro/activity)  
19. PyTubeStudio \- PyPI, 6월 24, 2025에 액세스, [https://pypi.org/project/PyTubeStudio/](https://pypi.org/project/PyTubeStudio/)  
20. Linux compatibility? :: VTube Studio 综合讨论 \- Steam Community, 6월 24, 2025에 액세스, [https://steamcommunity.com/app/1325860/discussions/0/3118147979136347291/?l=schinese](https://steamcommunity.com/app/1325860/discussions/0/3118147979136347291/?l=schinese)  
21. pixi-live2d-display-lipsyncpatch \- NPM, 6월 24, 2025에 액세스, [https://www.npmjs.com/package/pixi-live2d-display-lipsyncpatch](https://www.npmjs.com/package/pixi-live2d-display-lipsyncpatch)  
22. Models \- pixi-live2d-display, 6월 24, 2025에 액세스, [https://guansss.github.io/pixi-live2d-display/models/](https://guansss.github.io/pixi-live2d-display/models/)  
23. Complete Guide · guansss/pixi-live2d-display Wiki \- GitHub, 6월 24, 2025에 액세스, [https://github.com/guansss/pixi-live2d-display/wiki/Complete-Guide](https://github.com/guansss/pixi-live2d-display/wiki/Complete-Guide)  
24. Live2D Guide \- Open LLM Vtuber, 6월 24, 2025에 액세스, [http://docs.llmvtuber.com/en/docs/user-guide/live2d/](http://docs.llmvtuber.com/en/docs/user-guide/live2d/)  
25. homer\_1943/Open-LLM-VTuber \- Gitee, 6월 24, 2025에 액세스, [https://gitee.com/homer-1943/Open-LLM-VTuber](https://gitee.com/homer-1943/Open-LLM-VTuber)  
26. Project AIRI \- GitHub, 6월 24, 2025에 액세스, [https://github.com/proj-airi](https://github.com/proj-airi)