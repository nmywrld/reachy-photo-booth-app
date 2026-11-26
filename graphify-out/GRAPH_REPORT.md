# Graph Report - reachy-photo-booth-app  (2026-11-26)

## Corpus Check
- 331 files · ~147,510 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 64 file(s) not represented in the graph (top: (none) 30, .blenderAnim 17, .css 3)

## Summary
- 3833 nodes · 6610 edges · 258 communities (161 shown, 97 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 459 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `10b96a15`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Frontend Build Dependencies
- pygobject.h
- test_agent.py
- MirrorService
- time
- react_agent.py
- mirror
- Pre-generated Style Images
- ProceduralClip
- TTS Kokoro Engine
- service_executor.py
- Photo Booth State Machine
- UnifiedLLM
- AdaptiveFilter
- ServiceExecutor
- litellm.py
- Procedural Audio Effects
- Robot Position Debug Plots
- image_generation.py
- Robot Controller Compose
- CameraService
- App.tsx
- BaseConfig
- tracker-service/src/main.py
- Agent Service Compose
- Audio Envelopes & Generators
- Easing Curves
- .stop
- LLM Completion Client
- Compositor Audio Devices
- Interaction Event Handling
- Frequency Generator Effects
- Compositor Compose
- RobotLink
- STT Compose
- Interaction Manager Compose
- asyncio
- Robot Light Effects
- UI Server Runtime
- Animation Compositor Service
- model-wall
- Interaction Manager Config
- Animation DB Compose
- Remote Control Compose
- mirror_photo.py
- UI Server Compose
- Mock User Service
- Agent Service Main
- InteractionManagerService
- EulerAngles
- reachy_camera_probe.py
- Architecture Diagram
- Frontend TS App Config
- Producer
- MetricsService
- StreamTrack
- TTS Compose
- Tracker Compose
- Photobooth Workflow Config
- ProceduralClip
- Camera Compose
- play_positions.py
- Frontend TS Node Config
- tracker-service/src/main.py
- PhotoBoothReactAgentGraph
- MotionController
- animation-database-service/src/main.py
- Frontend Compose
- subscribe
- remote-control-service/src/main.py
- Look-At Behaviour
- Frontend API Types
- animation-compositor-service/src/main.py
- Workspace Packages
- Template Compose
- set_mirror_style
- ._later
- End Interaction Tool
- Stylizer
- Audio Debug Docs
- Remote Control Events
- Topic
- Metrics Compose
- Pixelated Image Hook
- Deployment Instructions
- ReachyBoothCamera
- UiServerService
- PhotoGate
- GPU Deploy Resources
- MinIO Infrastructure
- Agent Service
- reachy_booth_camera.py
- classnames
- Animated Border UI
- Agent Tool Call Tests
- Animation
- LLM Params Config
- Clock
- Session
- Redpanda Console Config
- Service
- reachy_booth/main.py
- completion_client_langchain
- Redpanda (Kafka broker)
- Speech & Latency Docs
- TrackerService
- Kiosk Frontend Docs
- .on_user_detection
- model_wall.py
- flux_load.py
- Compose Config Mounts
- Volume Init Container
- Robot Utterances Data
- RobotStateMachine
- Design
- Agent Prompt Config
- reachy_camera_probe.py
- react
- Shared Volumes
- Photobooth Root Config
- Agent MinIO Settings
- DetectionResult
- resources
- Root Compose Includes
- Infra Service Commands
- TTS Docs
- workmesh/__init__.py
- Range
- make_bot
- os
- Motor Config A
- Motor Config B
- Right Antenna Motor
- Stewart Motor 1
- Stewart Motor 2
- Stewart Motor 3
- Stewart Motor 4
- Stewart Motor 5
- Stewart Motor 6
- test_magic_mirror.py
- Compose Shared Configs
- Compose Healthchecks
- Compose Port Services A
- Compose Port Services B
- Detectron2Detector
- ReAct Agent Docs
- test_motion.py
- WahWah Effect
- BaseMetric
- Development Guide
- Transcript UI
- Agent Debug Override
- Image Gen Config
- Compositor Debug Override
- EventManager
- Animation DB Debug Override
- Camera Debug Override
- Coordinate System Diagram
- Interaction Debug Override
- Metrics Debug Override
- Remote Control Debug Override
- Hardware Serial Config
- Robot Controller Debug Override
- STT Debug Override
- Template Debug Override
- Robot
- TTS Debug Override
- Tracker Debug Override
- UI Server Debug Override
- Remote Control Page JS
- procedural_clips.py
- MyService
- Running the photo booth with a wireless Reachy Mini
- scripts
- Vite Env Types
- Root TS Config
- graphify Skill Docs
- LGTM Observability
- Root Project
- FrameGrabber
- register_routes
- dependencies
- guardrails_dataset.py
- AnimationData
- camera-service/src/configuration.py
- External applications: the reachy-bridge
- TrackFilters
- camera-service/src/main.py
- UiPhotoStateTests
- BitCrushEffect
- new-usage.md
- AudioConfig
- Every time you make changes
- audio-input.sh
- audio_debug.py
- main.js
- create_filter
- AgentServiceConfig
- ConditionTimeoutError
- RobotService
- create_hitl_callback
- filters.py
- test_tts_generates_audio_from_text
- config.py
- AudioConfig
- BaseLowPassFilter
- model-wall-service/src/main.py
- README.md
- DetectionFilter
- animation-compositor-service/src/configuration.py
- reachy_booth
- profile_conv.py
- ButterworthFilter
- ExponentialMovingAverageFilter
- PhotoBoothBotConfig
- FakeRobot
- extract_positions.py
- consumer_config
- audio-output.sh
- reachy-ip.sh

## God Nodes (most connected - your core abstractions)
1. `Frame` - 67 edges
2. `PhotoBoothBotStateMachine` - 60 edges
3. `subscribe()` - 57 edges
4. `Service` - 41 edges
5. `Producer` - 36 edges
6. `ProceduralClip` - 33 edges
7. `AnimationCompositorService` - 30 edges
8. `State` - 28 edges
9. `DetectionResult` - 27 edges
10. `InteractionManagerService` - 24 edges

## Surprising Connections (you probably didn't know these)
- `Styles` --references--> `set_mirror_style()`  [INFERRED]
  mirror-service/README.md → agent-service/workflows/photo_booth_agent/src/photo_booth_agent/tools/mirror.py
- `3. The app on the robot` --references--> `RobotLink`  [INFERRED]
  wireless-reachy-conn.md → reachy_booth/reachy_booth/link.py
- `Model inventory` --references--> `PhotoGate`  [INFERRED]
  i-want-to-convert-resilient-lightning.md → workmesh/src/workmesh/photo_gate.py
- `5. Settings you might change` --references--> `MirrorPhotoConfig`  [INFERRED]
  new-usage.md → agent-service/workflows/photo_booth_agent/src/photo_booth_agent/mirror_photo.py
- `Mirror service` --references--> `Frame`  [INFERRED]
  mirror-service/README.md → animation-compositor-service/src/clips/animations.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Composable procedural audio effect chain** — animation_database_service_src_audio_readme_frequencygenerator, animation_database_service_src_audio_readme_audioeffect, animation_database_service_src_audio_readme_wobbleeffect, animation_database_service_src_audio_readme_harmonicseffect, animation_database_service_src_audio_readme_distortioneffect, animation_database_service_src_audio_readme_echoeffect, animation_database_service_src_audio_readme_wahwaheffect, animation_database_service_src_audio_readme_tremoloeffect [EXTRACTED 1.00]
- **Agent-driven AI generation (Agent, LLM, Image Generator)** — docs_images_architecture_diagram_agent, docs_images_architecture_diagram_llm, docs_images_architecture_diagram_image_generator [EXTRACTED 1.00]
- **Reachy head translation coordinate axes** — docs_images_reachy_coordinate_system_top_view_reachy_head, docs_images_reachy_coordinate_system_top_view_head_position_x, docs_images_reachy_coordinate_system_top_view_head_position_y, docs_images_reachy_coordinate_system_top_view_reference_frame [EXTRACTED 1.00]
- **Photo capture gated on fresh person detection** — interaction_manager_service_readme_photo_capture_flow, interaction_manager_service_readme_photogate, tracker_service_readme_tracker_service, interaction_manager_service_readme_camera_capture_endpoint, interaction_manager_service_readme_center_user_timeout [EXTRACTED 1.00]
- **Audio output services sharing one sample rate** — animation_compositor_service_readme_animation_compositor_service, animation_database_service_readme_animation_database_service, animation_compositor_service_readme_shared_sample_rate, animation_compositor_service_readme_audio_config [EXTRACTED 1.00]
- **Workmesh service lifecycle and pub/sub pattern** — docs_writing_your_first_service_service, docs_writing_your_first_service_serviceexecutor, docs_writing_your_first_service_subscribe, docs_writing_your_first_service_ping_topic, docs_writing_your_first_service_typed_topic [EXTRACTED 1.00]
- **Robot animation and actuation** — docs_images_architecture_diagram_animation_database, docs_images_architecture_diagram_animation_compositor, docs_images_architecture_diagram_robot_controller, docs_images_architecture_diagram_robot_motion, docs_images_architecture_diagram_robot [INFERRED 0.75]
- **Voice conversation pipeline** — docs_images_architecture_diagram_microphone, docs_images_architecture_diagram_speech_to_text, docs_images_architecture_diagram_message_bus, docs_images_architecture_diagram_text_to_speech, docs_images_architecture_diagram_animation_compositor, docs_images_architecture_diagram_speaker [INFERRED 0.75]
- **Agent Tool Actions (whiteboard, Slack, search, human-in-the-loop)** — docs_images_remote_control_tool_readwhiteboard, docs_images_remote_control_tool_sendslackmessage, docs_images_remote_control_tool_internetsearch, docs_images_remote_control_tool_humanintheloop [INFERRED 0.75]
- **Robot Interaction Lifecycle Events (Start through End)** — docs_images_remote_control_event_start, docs_images_remote_control_event_wakeup, docs_images_remote_control_event_userappeared, docs_images_remote_control_event_userdisappeared, docs_images_remote_control_event_listen, docs_images_remote_control_event_think, docs_images_remote_control_event_end [INFERRED 0.75]
- **Kafka-based dev trigger scripts** — speech_to_text_service_scripts_trigger_stt, tracker_service_scripts_trigger_tracker, tracker_service_scripts_trigger_user_state, text_to_speech_service_scripts_trigger_tts [INFERRED 0.85]
- **Speech pipeline: STT -> user_utterance -> agent -> human_speech_request -> TTS -> clip_data -> compositor** — speech_to_text_service_readme_speech_to_text, metrics_service_readme_user_utterance_topic, metrics_service_readme_human_speech_request_topic, text_to_speech_service_readme_text_to_speech, metrics_service_readme_clip_data_topic, text_to_speech_service_readme_animation_compositor [INFERRED 0.85]

## Communities (258 total, 97 thin omitted)

### Community 0 - "Frontend Build Dependencies"
Cohesion: 0.09
Nodes (31): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, @tailwindcss/vite, @types/node, @types/react (+23 more)

### Community 1 - "pygobject.h"
Cohesion: 0.05
Nodes (31): PyGBoxed, PyGClassInitFunc, PyGClosure, _PyGClosure, callback, closure, exception_handler, extra_args (+23 more)

### Community 2 - "test_agent.py"
Cohesion: 0.09
Nodes (17): check_deflection(), check_refusal(), multi_tool_completion_checker(), condition(), parse_tool_calls(), remove_all_punctuation(), send_user_utterance(), test_agent_answers_question() (+9 more)

### Community 3 - "MirrorService"
Cohesion: 0.07
Nodes (8): MirrorConfig, main(), MirrorService, clean_style(), LatestSlot, RenderPause, sd_prompt(), StyleState

### Community 4 - "time"
Cohesion: 0.16
Nodes (9): change_volume(), look_at(), play_clip(), play_multiple(), producer_send(), Robot, stop_clip(), track() (+1 more)

### Community 6 - "mirror"
Cohesion: 0.05
Nodes (39): context, dockerfile, content, configs, config_mirror, source, target, llm (+31 more)

### Community 7 - "Pre-generated Style Images"
Cohesion: 0.05
Nodes (3): FloatingImages(), images, Sleeping()

### Community 8 - "ProceduralClip"
Cohesion: 0.08
Nodes (3): LookAtAnimation, ProceduralClip, TrackAnimation

### Community 9 - "TTS Kokoro Engine"
Cohesion: 0.11
Nodes (5): TextToSpeechServiceConfig, main(), TextToSpeechService, BaseTTSModel, KokoroTTSModel

### Community 11 - "Photo Booth State Machine"
Cohesion: 0.09
Nodes (3): PhotoBoothBotStateMachine, finding_user_sequence(), States

### Community 12 - "UnifiedLLM"
Cohesion: 0.10
Nodes (4): create_tool_from_basetool(), UnifiedLLM, convert_message_to_dict(), BaseMessage

### Community 14 - "ServiceExecutor"
Cohesion: 0.20
Nodes (11): main(), main(), main(), main(), main(), main(), main(), main() (+3 more)

### Community 15 - "litellm.py"
Cohesion: 0.09
Nodes (8): create_tool_from_callable(), ToolCall, ToolParameter, convert_delta_to_message_chunk(), convert_dict_to_message(), extract_and_parse_json(), get_item_type_schema(), get_parameter_schema()

### Community 16 - "Procedural Audio Effects"
Cohesion: 0.07
Nodes (8): AudioEffect, DistortionEffect, EchoEffect, NoiseEffect, PitchBendEffect, StutterEffect, TremoloEffect, WobbleEffect

### Community 17 - "Robot Position Debug Plots"
Cohesion: 0.24
Nodes (5): load_position_data(), main(), plot_positions(), plot_velocities(), save_highest_velocities()

### Community 18 - "image_generation.py"
Cohesion: 0.05
Nodes (27): MinioConfig, InvalidImageError, square_to_landscape(), EndInteractionInput, HITLFunctionInput, StartInteractionInput, look_at_human_tool(), _inner() (+19 more)

### Community 19 - "Robot Controller Compose"
Cohesion: 0.06
Nodes (31): condition, context, dockerfile, content, configs, config_robot_controller, source, target (+23 more)

### Community 21 - "App.tsx"
Cohesion: 0.11
Nodes (17): App(), BigMessage(), BigMessageProps, CapturedImage(), CapturedImageProps, FullScreen(), FullScreenProps, useAppState() (+9 more)

### Community 22 - "BaseConfig"
Cohesion: 0.13
Nodes (10): InteractionManagerConfig, MetricsServiceConfig, AudioConfig, EndpointingConfig, RivaConfig, Seconds, SpeechToTextConfig, VadConfig (+2 more)

### Community 23 - "tracker-service/src/main.py"
Cohesion: 0.17
Nodes (3): BaseDetector, create_detector(), SSDLiteDetector

### Community 24 - "Agent Service Compose"
Cohesion: 0.07
Nodes (29): build, container_name, depends_on, develop, environment, healthcheck, image, restart (+21 more)

### Community 26 - "Easing Curves"
Cohesion: 0.08
Nodes (27): ease_in_bounce(), ease_in_circ(), ease_in_elastic(), ease_in_expo(), ease_in_out_back(), ease_in_out_bounce(), ease_in_out_circ(), ease_in_out_cubic() (+19 more)

### Community 28 - "LLM Completion Client"
Cohesion: 0.12
Nodes (3): CompletionClient, LLMResponse, Tool

### Community 29 - "Compositor Audio Devices"
Cohesion: 0.10
Nodes (5): create_animation_frames(), create_robot_message(), find_output_device_index(), validate_audio_settings(), find_device_index()

### Community 30 - "Interaction Event Handling"
Cohesion: 0.11
Nodes (3): UserTrackerStateMachine, Config, States

### Community 31 - "Frequency Generator Effects"
Cohesion: 0.17
Nodes (11): FrequencyGenerator, HarmonicsEffect, PulseEffect, SmoothingEffect, generate_body_angle_sound(), generate_head_pitch_sound(), generate_head_roll_sound(), generate_head_yaw_sound() (+3 more)

### Community 32 - "Compositor Compose"
Cohesion: 0.07
Nodes (29): content, build, configs, container_name, depends_on, develop, devices, environment (+21 more)

### Community 33 - "RobotLink"
Cohesion: 0.13
Nodes (4): connect_localhost(), FixedLink, RobotLink, test_link_retries_until_the_daemon_is_reachable()

### Community 34 - "STT Compose"
Cohesion: 0.07
Nodes (27): context, dockerfile, content, configs, config_speech_to_text, source, target, redpanda (+19 more)

### Community 35 - "Interaction Manager Compose"
Cohesion: 0.07
Nodes (26): condition, context, dockerfile, content, configs, config_interaction_manager, source, target (+18 more)

### Community 36 - "asyncio"
Cohesion: 0.07
Nodes (10): main(), producer_send(), main(), Transcription, main(), producer_send(), Robot, main() (+2 more)

### Community 38 - "UI Server Runtime"
Cohesion: 0.10
Nodes (11): lifespan(), State, AskHuman, BoundingCircle, FillCircleAnimation, GenerateImage, GreetUser, LookAtHuman (+3 more)

### Community 40 - "model-wall"
Cohesion: 0.11
Nodes (18): context, dockerfile, redpanda, resources, build, cap_add, container_name, depends_on (+10 more)

### Community 41 - "Interaction Manager Config"
Cohesion: 0.18
Nodes (5): AnimationConfig, LightConfig, Range, TrackingConfig, VoiceConfig

### Community 42 - "Animation DB Compose"
Cohesion: 0.08
Nodes (23): build, configs, container_name, depends_on, develop, image, restart, volumes (+15 more)

### Community 43 - "Remote Control Compose"
Cohesion: 0.08
Nodes (23): context, dockerfile, content, configs, config_remote_control, source, target, redpanda (+15 more)

### Community 44 - "mirror_photo.py"
Cohesion: 0.16
Nodes (4): flux_prompt(), _minio(), MirrorPhotoConfig, MirrorPhotoService

### Community 45 - "UI Server Compose"
Cohesion: 0.08
Nodes (23): context, dockerfile, content, configs, config_ui_server, source, target, redpanda (+15 more)

### Community 46 - "Mock User Service"
Cohesion: 0.11
Nodes (3): MockUserService, run_mock_service(), main()

### Community 49 - "EulerAngles"
Cohesion: 0.10
Nodes (5): blend_multiple_frames(), Degrees, EulerAngles, lerp(), slerp()

### Community 50 - "reachy_camera_probe.py"
Cohesion: 0.06
Nodes (22): Configuration (`/config.yaml`), Licence, Mirror service, Performance (GB10, GPT-OSS 20B and FLUX.1 Kontext loaded), Styles, Testing without the robot, fetch_daemon_info(), main() (+14 more)

### Community 51 - "Architecture Diagram"
Cohesion: 0.11
Nodes (22): Architecture Diagram, Agent (NeMo Agent Toolkit), Animation Compositor, Animation Database, Browser, Camera Service, Camera Device, Image Generator (FLUX.1 Kontext) (+14 more)

### Community 52 - "Frontend TS App Config"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 54 - "Producer"
Cohesion: 0.09
Nodes (8): KafkaAsyncCallbackHandler, play_clip_async(), producer_send(), producer(), restart_agent(), producer_send(), ProducerConfig, Producer

### Community 55 - "MetricsService"
Cohesion: 0.15
Nodes (4): MetricsService, PendingTTSRequest, TTSLatencyMetric, TTSRateMetric

### Community 56 - "StreamTrack"
Cohesion: 0.15
Nodes (4): Design, FrameSource, square_crop(), StreamTrack

### Community 58 - "TTS Compose"
Cohesion: 0.09
Nodes (21): context, dockerfile, redpanda, resources, watch, condition, devices, reservations (+13 more)

### Community 59 - "Tracker Compose"
Cohesion: 0.08
Nodes (25): context, dockerfile, redpanda, resources, watch, condition, devices, reservations (+17 more)

### Community 60 - "Photobooth Workflow Config"
Cohesion: 0.10
Nodes (20): workflow, additional_instructions, allow_null_tool, greet_message, human_feedback_tool, llm_name, max_history, max_retries (+12 more)

### Community 62 - "Camera Compose"
Cohesion: 0.08
Nodes (25): context, dockerfile, build, configs, container_name, depends_on, develop, devices (+17 more)

### Community 64 - "Frontend TS Node Config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+11 more)

### Community 66 - "PhotoBoothReactAgentGraph"
Cohesion: 0.06
Nodes (10): StructuredAgentAction, type_name(), PhotoBoothReactAgentGraph, _trim_messages(), photo_booth_react_function(), _response_fn(), _str_api_fn(), PhotoBoothReactWorkflowConfig (+2 more)

### Community 67 - "MotionController"
Cohesion: 0.15
Nodes (3): ReachyBooth, MotionController, test_controller_streams_latest_frame_and_pauses()

### Community 68 - "animation-database-service/src/main.py"
Cohesion: 0.11
Nodes (4): convert_audio(), LRUCacheDict, DatabaseConfig, Model

### Community 69 - "Frontend Compose"
Cohesion: 0.11
Nodes (17): condition, args, context, dockerfile, agent, watch, services, ui (+9 more)

### Community 70 - "subscribe"
Cohesion: 0.09
Nodes (7): AnimationDatabaseService, AnimationData, produces(), decorator(), wrapper(), subscribe(), decorator()

### Community 71 - "remote-control-service/src/main.py"
Cohesion: 0.17
Nodes (4): main(), RemoteControlConfig, RemoteControlService, TriggerCommandRequest

### Community 72 - "Look-At Behaviour"
Cohesion: 0.17
Nodes (4): Degrees, KeyPosition, Position, Robot

### Community 73 - "Frontend API Types"
Cohesion: 0.11
Nodes (17): AbortMessage, Animation, AppState, AskHuman, BaseMessage, BoundingCircle, COLOR, FillCircleAnimation (+9 more)

### Community 76 - "Workspace Packages"
Cohesion: 0.12
Nodes (16): agent, animation-compositor, animation-database, camera, interaction-manager, metrics, model-wall, photo-booth-agent (+8 more)

### Community 77 - "Template Compose"
Cohesion: 0.13
Nodes (14): context, dockerfile, watch, build, container_name, develop, environment, image (+6 more)

### Community 78 - "set_mirror_style"
Cohesion: 0.36
Nodes (5): set_mirror_style(), _arun(), SetMirrorStyleConfig, take_mirror_photo(), TakeMirrorPhotoConfig

### Community 80 - "End Interaction Tool"
Cohesion: 0.11
Nodes (12): NoResponseError, SuggestionMessage, end_interaction(), _arun(), EndInteractionToolConfig, hitl_function(), _arun(), HITLFunctionConfig (+4 more)

### Community 81 - "Stylizer"
Cohesion: 0.11
Nodes (4): _CompiledUNet, _Pipeline, Stylizer, _UNetArgs

### Community 82 - "Audio Debug Docs"
Cohesion: 0.12
Nodes (14): plot_debug_positions.py script, Procedural Audio Generation (motor sounds), test_procedural_audio.py script, AudioEffect (base class), create_audio_debug_plot() (audio_debug), DistortionEffect, easing_curves module, EchoEffect (+6 more)

### Community 83 - "Remote Control Events"
Cohesion: 0.15
Nodes (14): End Event, Listen Event, Start Event, Think Event, UserAppeared Event, UserDisappeared Event, WakeUp Event, Remote Control Output Log Area (+6 more)

### Community 84 - "Topic"
Cohesion: 0.14
Nodes (9): listen_only(), main(), _arun(), _wait_for_photo(), wait_for_event(), _wait_for_event(), ConsumerConfig, Consumer (+1 more)

### Community 85 - "Metrics Compose"
Cohesion: 0.14
Nodes (13): context, dockerfile, watch, build, container_name, develop, image, restart (+5 more)

### Community 86 - "Pixelated Image Hook"
Cohesion: 0.23
Nodes (8): canvasDimensions, usePixelatedImage(), ImageGeneration(), ImageGenerationProps, TEXTS, TextCarousel(), TextCarouselProps, shuffleArray()

### Community 87 - "Deployment Instructions"
Cohesion: 0.10
Nodes (23): Animation Compositor Service, audio_config (output_device_index_or_name, sample_rate), list_sound_devices.py script, Animation Database Service, Blender Animation Library (assets/animLibrary), Procedural Animation Generation (look_at, tracking), test_clips.py script, camera_serial_or_url config (+15 more)

### Community 89 - "UiServerService"
Cohesion: 0.09
Nodes (4): clear_task(), clear_task(), UiServerService, update_callback()

### Community 90 - "PhotoGate"
Cohesion: 0.14
Nodes (7): AsyncTests, consume(), fresh_frame(), detection(), GateTests, load_method(), PhotoGate

### Community 91 - "GPU Deploy Resources"
Cohesion: 0.18
Nodes (11): llm, condition, container_name, depends_on, environment, hostname, image, ports (+3 more)

### Community 92 - "MinIO Infrastructure"
Cohesion: 0.18
Nodes (11): MINIO_ROOT_PASSWORD, MINIO_ROOT_USER, disable, command, container_name, environment, healthcheck, image (+3 more)

### Community 93 - "Agent Service"
Cohesion: 0.16
Nodes (21): Agent Service, EXTERNAL_MINIO_BASE_URL env var, mock_user.py script, Photo Booth Assistant config (photobooth.yml), trigger_agent_restart.py script, OpenTelemetry endpoints (lgtm-otel:4317/4318), .env config (NVIDIA_API_KEY, HF_TOKEN), QR-code sharing on local network (+13 more)

### Community 95 - "classnames"
Cohesion: 0.12
Nodes (8): classnames, BinocularsProps, Crosshair(), CrosshairProps, MirrorPhotoCardProps, STATUS_TEXT, QRCodeProps, VideoFeedProps

### Community 96 - "Animated Border UI"
Cohesion: 0.35
Nodes (7): FillCircleBorder(), FillCircleBorderProps, LightBorder(), LightBorderProps, AnimationProps, COLORS, StaticBorder()

### Community 98 - "Animation"
Cohesion: 0.09
Nodes (6): Animation, AnimationClip, AudioClip, ProceduralAnimation, StaticAnimation, StaticClip

### Community 99 - "LLM Params Config"
Cohesion: 0.17
Nodes (12): allowed_openai_params, reasoning_effort, additional_kwargs, api_key, base_url, max_retries, max_tokens, model_name (+4 more)

### Community 100 - "Clock"
Cohesion: 0.21
Nodes (3): Clock, RenderPauseTests, StyleStateTests

### Community 101 - "Session"
Cohesion: 0.21
Nodes (6): connect(), AbortMessage, AppState, ShutterMessage, Signalling, Session

### Community 102 - "Redpanda Console Config"
Cohesion: 0.17
Nodes (12): CONFIG_FILEPATH, CONSOLE_CONFIG_FILE, command, container_name, depends_on, entrypoint, environment, image (+4 more)

### Community 105 - "completion_client_langchain"
Cohesion: 0.18
Nodes (3): completion_client_langchain(), completion_client_provider(), CompletionClientConfig

### Community 106 - "Redpanda (Kafka broker)"
Cohesion: 0.08
Nodes (32): Interaction Manager Service README, Agent Service (LLM-powered), Camera /capture endpoint frame-index check, center_user_timeout, Interaction Manager, workmesh.photo_gate.PhotoGate, Redpanda (Kafka broker), Robot Utterances (robot_utterances.yaml) (+24 more)

### Community 107 - "Speech & Latency Docs"
Cohesion: 0.18
Nodes (11): e2e.latency histogram, user_utterance_topic (UserUtterance), ReSpeaker XVF3800 4-Mic Array, udev rules 99-reachy-mini.rules, speaker_setup.sh script, Speech-to-Text Service README, input_device_index_or_name / audio_config.sample_rate, list_sound_devices.py (+3 more)

### Community 108 - "TrackerService"
Cohesion: 0.10
Nodes (3): FilterConfig, TrackerConfig, TrackerService

### Community 109 - "Kiosk Frontend Docs"
Cohesion: 0.20
Nodes (9): ui-frontend AGENTS.md (Cursor Rules), FloatingImages component, React 19 / Vite 7 / Tailwind CSS 4 / TypeScript, ui-frontend index.html (Vite entry), Spark & Reachy Photo Booth UI README, UI Server WebRTC test page (index.html), WebRTC Signalling over WebSocket (/ws), UI Server Service README (+1 more)

### Community 110 - ".on_user_detection"
Cohesion: 0.29
Nodes (4): convert_bits_per_sample(), Degrees, EulerAngle, TrackingData

### Community 111 - "model_wall.py"
Cohesion: 0.31
Nodes (4): _report(), report_end(), report_start(), _send()

### Community 112 - "flux_load.py"
Cohesion: 0.60
Nodes (3): run(), full_test.sh script, run.sh script

### Community 113 - "Compose Config Mounts"
Cohesion: 0.22
Nodes (11): source, target, configs, container_name, image, ports, restart, volumes (+3 more)

### Community 114 - "Volume Init Container"
Cohesion: 0.17
Nodes (12): init-volumes, container_name, depends_on, environment, hostname, image, ports, restart (+4 more)

### Community 115 - "Robot Utterances Data"
Cohesion: 0.14
Nodes (13): demo_information, facts, performance, generate_image, completed, look_at_human, completed, started (+5 more)

### Community 118 - "Design"
Cohesion: 0.33
Nodes (5): Context, Magic Mirror conversion: models and plan, Model inventory, Risks, Verification

### Community 119 - "Agent Prompt Config"
Cohesion: 0.14
Nodes (14): prompt, _type, _type, functions, ask_human, farewell_user, greet_user, look_at_human (+6 more)

### Community 120 - "reachy_camera_probe.py"
Cohesion: 0.09
Nodes (7): encode_jpeg(), letterbox(), main(), publish(), Source, from_cv2_to_torch(), from_torch_to_cv2()

### Community 121 - "react"
Cohesion: 0.18
Nodes (7): react, Countdown(), CountdownProps, useWebRTC(), UseWebRTCOptions, wait(), WakeUpAnimation()

### Community 122 - "Shared Volumes"
Cohesion: 0.18
Nodes (11): volumes, cache, grafana, hf, loki, minio, nim, phoenix_data (+3 more)

### Community 123 - "Photobooth Root Config"
Cohesion: 0.22
Nodes (8): general, telemetry, llms, endpoint, project, _type, tracing, phoenix

### Community 124 - "Agent MinIO Settings"
Cohesion: 0.22
Nodes (9): access_key, base_url, bucket, create_bucket, image_base_url, internal_base_url, secret_key, secure (+1 more)

### Community 126 - "resources"
Cohesion: 0.33
Nodes (6): resources, deploy, deploy, devices, reservations, deploy

### Community 127 - "Root Compose Includes"
Cohesion: 0.22
Nodes (8): include, command, container_name, image, restart, volumes, services, init-volumes

### Community 128 - "Infra Service Commands"
Cohesion: 0.20
Nodes (10): command, container_name, environment, hostname, image, ipc, ports, restart (+2 more)

### Community 129 - "TTS Docs"
Cohesion: 0.16
Nodes (14): talkingForward Speech Animation, Metrics Service README, clip_data_topic (ClipData), human_speech_request_topic (HumanSpeechRequest), LGTM OpenTelemetry Collector (Grafana), Metrics Service, tts.latency histogram, tts.rate histogram (+6 more)

### Community 130 - "workmesh/__init__.py"
Cohesion: 0.21
Nodes (4): dict_to_protobuf_map(), protobuf_map_to_dict(), protobuf_value_to_python(), python_to_protobuf_value()

### Community 132 - "make_bot"
Cohesion: 0.31
Nodes (3): bot_env(), make_bot(), ShutterTests

### Community 134 - "Motor Config A"
Cohesion: 0.25
Nodes (8): id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit, body_rotation

### Community 135 - "Motor Config B"
Cohesion: 0.25
Nodes (8): id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit, left_antenna

### Community 136 - "Right Antenna Motor"
Cohesion: 0.25
Nodes (8): right_antenna, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 137 - "Stewart Motor 1"
Cohesion: 0.25
Nodes (8): stewart_1, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 138 - "Stewart Motor 2"
Cohesion: 0.25
Nodes (8): stewart_2, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 139 - "Stewart Motor 3"
Cohesion: 0.25
Nodes (8): stewart_3, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 140 - "Stewart Motor 4"
Cohesion: 0.25
Nodes (8): stewart_4, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 141 - "Stewart Motor 5"
Cohesion: 0.25
Nodes (8): stewart_5, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 142 - "Stewart Motor 6"
Cohesion: 0.25
Nodes (8): stewart_6, id, lower_limit, offset, pid, return_delay_time, shutdown_error, upper_limit

### Community 143 - "test_magic_mirror.py"
Cohesion: 0.13
Nodes (5): FrameSourceTests, LatestSlotTests, load_module(), Status, UiMessageTests

### Community 144 - "Compose Shared Configs"
Cohesion: 0.29
Nodes (7): configs, otel, redpanda, script_llm, content, content, content

### Community 145 - "Compose Healthchecks"
Cohesion: 0.57
Nodes (7): start_interval, start_period, test, healthcheck, healthcheck, healthcheck, healthcheck

### Community 146 - "Compose Port Services A"
Cohesion: 0.29
Nodes (7): container_name, environment, image, ports, restart, volumes, phoenix

### Community 147 - "Compose Port Services B"
Cohesion: 0.29
Nodes (7): command, container_name, image, ports, restart, volumes, redpanda

### Community 148 - "Detectron2Detector"
Cohesion: 0.12
Nodes (3): ByteTrackConfig, ByteTrackDetector, Detectron2Detector

### Community 149 - "ReAct Agent Docs"
Cohesion: 0.40
Nodes (4): Agent State (messages + agent_scratchpad), PhotoBoothReactWorkflowConfig, Tool call Kafka events (TOOL_CALL_STARTED/COMPLETED/FAILED), NeMo Agent Toolkit

### Community 150 - "test_motion.py"
Cohesion: 0.11
Nodes (14): get_format_from_width(), ws_motion(), measured_pose(), MotionStats, parse_frame(), pose_to_dict(), pose_to_targets(), step_towards() (+6 more)

### Community 153 - "Development Guide"
Cohesion: 0.19
Nodes (12): Development Guide, Getting Started Guide, Hot Reload (docker compose --watch), VS Code container debugging (service-debug.override.yaml), Workmesh framework, ping_topic / Ping protobuf message, workmesh Service base class, Service template scaffolding (template/) (+4 more)

### Community 154 - "Transcript UI"
Cohesion: 0.40
Nodes (4): COLORS, getScrollDuration(), Transcript(), TranscriptProps

### Community 155 - "Agent Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, agent

### Community 156 - "Image Gen Config"
Cohesion: 0.40
Nodes (5): generate_image, base_url, disable_safety_checker, steps, _type

### Community 157 - "Compositor Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, animation-compositor

### Community 159 - "Animation DB Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, animation-database

### Community 160 - "Camera Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, camera

### Community 161 - "Coordinate System Diagram"
Cohesion: 0.80
Nodes (5): Reachy Coordinate System Top View Diagram, head_position_x, head_position_y, Reachy Mini Head (top view), XY Reference Frame (X red down, Y green right)

### Community 162 - "Interaction Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, interaction-manager

### Community 163 - "Metrics Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, metrics

### Community 164 - "Remote Control Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, remote-control

### Community 165 - "Hardware Serial Config"
Cohesion: 0.40
Nodes (4): motors, serial, baudrate, version

### Community 166 - "Robot Controller Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, robot-controller

### Community 167 - "STT Debug Override"
Cohesion: 0.40
Nodes (4): services, speech-to-text, command, volumes

### Community 168 - "Template Debug Override"
Cohesion: 0.40
Nodes (4): command, volumes, services, SERVICE_NAME

### Community 170 - "TTS Debug Override"
Cohesion: 0.40
Nodes (4): services, text-to-speech, command, volumes

### Community 171 - "Tracker Debug Override"
Cohesion: 0.40
Nodes (4): services, tracker, command, volumes

### Community 172 - "UI Server Debug Override"
Cohesion: 0.40
Nodes (4): services, ui-server, command, volumes

### Community 173 - "Remote Control Page JS"
Cohesion: 0.33
Nodes (7): remote_control_command_topic (RemoteControlCommand), GET /api/commands, POST /api/trigger-command, loadCommands(), setupKeyboardShortcuts(), triggerCommand(), messages.proto (Protocol Buffers)

### Community 176 - "Running the photo booth with a wireless Reachy Mini"
Cohesion: 0.15
Nodes (13): 1. Prerequisites, 2. Check the app before publishing, 3. Publish it to Hugging Face, 4. Install and run it on the robot, 5. Point the booth at the robot, 6. Verify, App API reference, Files (+5 more)

### Community 177 - "scripts"
Cohesion: 0.40
Nodes (5): scripts, build, dev, lint, preview

### Community 194 - "register_routes"
Cohesion: 0.20
Nodes (8): register_routes(), connected_robot(), scripted_move(), sleep(), status(), stream(), wake_up(), zero()

### Community 195 - "dependencies"
Cohesion: 0.22
Nodes (7): react-dom, tailwindcss, dependencies, classnames@^2.5.1, react@^19.2.3, react-dom@^19.2.3, tailwindcss@^4.1.17

### Community 196 - "guardrails_dataset.py"
Cohesion: 0.25
Nodes (4): get_critical_test_cases(), get_test_cases_by_category(), get_test_cases_by_severity(), GuardrailTestCase

### Community 197 - "AnimationData"
Cohesion: 0.20
Nodes (3): Animation, JointData1D, JointData2D

### Community 198 - "camera-service/src/configuration.py"
Cohesion: 0.20
Nodes (4): CameraConfig, ImageEncoding, Resolution, Robot

### Community 199 - "External applications: the reachy-bridge"
Cohesion: 0.17
Nodes (11): 1. Commands: forwarding to the robot, 2. Data: receiving from the robot, 3. The app on the robot, Call the bridge from your application, Configure the bridge, Connecting from the Hermes (OpenShell) sandbox, Connecting to the wireless Reachy, External applications: the reachy-bridge (+3 more)

### Community 202 - "UiPhotoStateTests"
Cohesion: 0.26
Nodes (3): load_functions(), PresenceTests, UiPhotoStateTests

### Community 205 - "new-usage.md"
Cohesion: 0.25
Nodes (7): 1. One-time setup, 2. Start the booth, 3. Open the screens, 4. What a visitor does, 6. Testing without the robot, 7. If something's off, Not tested yet

### Community 207 - "Every time you make changes"
Cohesion: 0.25
Nodes (7): 1. Edit and commit in the parent repo (normal workflow), 2. Copy the changes into the HF clone, 3. Commit and push from the HF clone, Every time you make changes, One-time setup: create the HF push clone, Quick reference, Syncing `reachy_booth/` to Hugging Face

### Community 208 - "audio-input.sh"
Cohesion: 0.70
Nodes (4): dc(), host_default(), list_sources(), audio-input.sh script

### Community 212 - "main.js"
Cohesion: 0.29
Nodes (5): daemonEl, healthEl, moveResult, preview, previewBtn

### Community 217 - "RobotService"
Cohesion: 0.14
Nodes (3): RobotControllerConfig, frame_to_dict(), RobotService

### Community 223 - "config.py"
Cohesion: 0.06
Nodes (8): main(), mirror_photo_config(), Robot, BoothAppConfig, Robot, pytest_addoption(), Robot, OffsetType

### Community 230 - "model-wall-service/src/main.py"
Cohesion: 0.06
Nodes (13): ActivityTracker, ModelWallConfig, container_for_pid(), GpuSampler, memory_by_container(), parse_meminfo(), _read(), index() (+5 more)

### Community 237 - "animation-compositor-service/src/configuration.py"
Cohesion: 0.18
Nodes (3): AudioConfig, CompositorConfig, Robot

### Community 247 - "PhotoBoothBotConfig"
Cohesion: 0.40
Nodes (3): PhotoBoothBotConfig, RobotConfig, 5. Settings you might change

### Community 254 - "audio-output.sh"
Cohesion: 0.83
Nodes (3): dc(), list_sinks(), audio-output.sh script

## Ambiguous Edges - Review These
- `Workmesh Messaging Library` → `Service Template README`  [AMBIGUOUS]
  template/README.md · relation: conceptually_related_to
- `Image Generator (FLUX.1 Kontext)` → `MinIO`  [AMBIGUOUS]
  docs/images/architecture-diagram.png · relation: shares_data_with

## Knowledge Gaps
- **96 isolated node(s):** `callback`, `closure`, `exception_handler`, `extra_args`, `swap_data` (+91 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1764 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **97 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Service` connect `Service` to `workmesh/__init__.py`, `MirrorService`, `TTS Kokoro Engine`, `service_executor.py`, `CameraService`, `BaseConfig`, `BaseMetric`, `.stop`, `asyncio`, `Animation Compositor Service`, `mirror_photo.py`, `Agent Service Main`, `InteractionManagerService`, `MyService`, `Producer`, `MetricsService`, `StreamTrack`, `subscribe`, `remote-control-service/src/main.py`, `Topic`, `UiServerService`, `RobotService`, `model-wall-service/src/main.py`, `TrackerService`, `RobotStateMachine`?**
  _High betweenness centrality (0.071) - this node is a cross-community bridge._
- **Are the 10 inferred relationships involving `Frame` (e.g. with `BlendingAnimationClip` and `LookAtAnimation`) actually correct?**
  _`Frame` has 10 INFERRED edges - model-reasoned connections that need verification._
- **What connects `callback`, `closure`, `exception_handler` to the rest of the system?**
  _96 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend Build Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.09269162210338681 - nodes in this community are weakly interconnected._
- **Why does `Design` connect `StreamTrack` to `Service`, `Pixelated Image Hook`, `tracker-service/src/main.py`, `Design`, `PhotoGate`, `ProceduralClip`?**
  _High betweenness centrality (0.064) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Workmesh Messaging Library` and `Service Template README`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._
- **What is the exact relationship between `Image Generator (FLUX.1 Kontext)` and `MinIO`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._