# Graph Report - reachy-photo-booth-app  (2026-11-06)

## Corpus Check
- 257 files · ~117,611 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 53 file(s) not represented in the graph (top: (none) 25, .blenderAnim 17, .example 2)

## Summary
- 3083 nodes · 5256 edges · 215 communities (144 shown, 71 thin omitted)
- Extraction: 93% EXTRACTED · 7% INFERRED · 0% AMBIGUOUS · INFERRED: 363 edges (avg confidence: 0.89)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `5181b3ae`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- Frontend Build Dependencies
- Agent Guardrail Tests
- procedural_clips.py
- PhotoGate
- Agent Structured Output
- Tracker Detection Pipeline
- Pre-generated Style Images
- AudioClip
- TTS Kokoro Engine
- STT Riva Client
- Photo Booth State Machine
- LLM Tool Abstraction
- filters.py
- subscribe
- litellm.py
- Procedural Audio Effects
- Robot Position Debug Plots
- Image Generation Tool
- Robot Controller Compose
- robot-controller-service/src/utils.py
- Frontend App & Messages
- Agent HITL & MinIO Config
- tracker-service/src/main.py
- Agent Service Compose
- Audio Envelopes & Generators
- Easing Curves
- ConsumerConfig
- LLM Completion Client
- Compositor Audio Devices
- Interaction Event Handling
- Frequency Generator Effects
- Compositor Compose
- config.py
- STT Compose
- Interaction Manager Compose
- KafkaAsyncCallbackHandler
- Robot Light Effects
- UI Server Runtime
- Animation Compositor Service
- Robot Utterance Manager
- Interaction Manager Config
- Animation DB Compose
- Remote Control Compose
- ByteTrack Detector
- UI Server Compose
- Mock User Service
- Agent Service Main
- Interaction Manager Service
- Service
- react_function.py
- Architecture Diagram
- Frontend TS App Config
- AnimationDatabaseService
- Camera Service Handler
- Metrics Event Consumers
- WebRTC Session
- TTS Compose
- Tracker Compose
- Photobooth Workflow Config
- ProceduralClip
- Camera Compose
- Event Manager
- Frontend TS Node Config
- State Enter Handlers
- react_function.py
- E2E Latency Metric
- Service Template
- Frontend Compose
- animation-database-service/src/main.py
- Remote Control Server
- Look-At Behaviour
- Frontend API Types
- Clip Test Script
- AsyncTests
- Workspace Packages
- Template Compose
- Robot Controller Shutdown
- photo_booth_agent/utils.py
- End Interaction Tool
- llm/utils.py
- Audio Debug Docs
- Remote Control Events
- service.py
- Metrics Compose
- Pixelated Image Hook
- Agent & Camera Docs
- animations.py
- Compositor Audio Config
- Animation Data Model
- GPU Deploy Resources
- MinIO Infrastructure
- Getting Started Docs
- Redpanda & Remote Control Docs
- Capture & Countdown UI
- Animated Border UI
- Agent Tool Call Tests
- UI Server Status Models
- LLM Params Config
- Agent Exceptions
- animation-database-service/src/utils.py
- Redpanda Console Config
- Hardware & Model Overview
- Service Telemetry
- Interaction & Robot Docs
- Photo Capture Flow Docs
- Speech & Latency Docs
- Kiosk Frontend Docs
- robot-controller-service/src/configuration.py
- DetectionFilter
- TrackAnimation
- Compose Config Mounts
- Volume Init Container
- Robot Utterances Data
- Guardrails Dataset
- Tracker Config
- Agent Prompt Config
- Producer
- Shared Volumes
- Photobooth Root Config
- Agent MinIO Settings
- Shared Sample Rate Docs
- ServiceExecutor
- Root Compose Includes
- Infra Service Commands
- TTS Docs
- ReAct Agent Core
- Compositor Range Model
- Development Guide
- Motor Config A
- Motor Config B
- Right Antenna Motor
- Stewart Motor 1
- Stewart Motor 2
- Stewart Motor 3
- Stewart Motor 4
- Stewart Motor 5
- Stewart Motor 6
- Agent Service Config
- Compose Shared Configs
- Compose Healthchecks
- Compose Port Services A
- Compose Port Services B
- Metrics Docs
- ReAct Agent Docs
- WahWah Effect
- Animation DB Audio Config
- Workmesh Framework Docs
- Transcript UI
- Agent Debug Override
- Image Gen Config
- Compositor Debug Override
- AudioMixer
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
- Test Timeout Errors
- TTS Debug Override
- Tracker Debug Override
- UI Server Debug Override
- Remote Control Page JS
- Wake-Up Animation UI
- MinIO QR Sharing
- audio_utility.py
- Vite Env Types
- Root TS Config
- graphify Skill Docs
- LGTM Observability
- Root Project
- camera-service/src/configuration.py
- parse_tool_calls
- ui-server-service/src/main.py
- trigger_tts.py
- .__init__
- Connecting applications to the wireless Reachy
- audio_debug.py
- DistortionEffect
- AudioConfig
- NoiseEffect
- TremoloEffect
- EchoEffect

## God Nodes (most connected - your core abstractions)
1. `PhotoBoothBotStateMachine` - 59 edges
2. `Frame` - 53 edges
3. `subscribe()` - 45 edges
4. `Service` - 37 edges
5. `Producer` - 33 edges
6. `ProceduralClip` - 33 edges
7. `AnimationCompositorService` - 30 edges
8. `InteractionManagerService` - 26 edges
9. `DetectionResult` - 25 edges
10. `State` - 22 edges

## Surprising Connections (you probably didn't know these)
- `Event-driven message bus architecture` --conceptually_related_to--> `Redpanda message broker`  [INFERRED]
  docs/overview.md → README.md
- `workmesh.photo_gate.PhotoGate` --semantically_similar_to--> `Presence State Machine (appeared/disappeared)`  [INFERRED] [semantically similar]
  interaction-manager-service/README.md → tracker-service/README.md
- `src/configuration.py defaults overridden by compose.yaml` --conceptually_related_to--> `audio_config (output_device_index_or_name, sample_rate)`  [INFERRED]
  docs/development.md → animation-compositor-service/README.md
- `Velocity-driven custom volume/pitch envelopes` --semantically_similar_to--> `plot_debug_positions.py script`  [INFERRED] [semantically similar]
  animation-database-service/src/audio/README.md → animation-compositor-service/README.md
- `OpenTelemetry endpoints (lgtm-otel:4317/4318)` --semantically_similar_to--> `Arize Phoenix tracing`  [INFERRED] [semantically similar]
  docs/getting-started.md → README.md

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

## Communities (215 total, 71 thin omitted)

### Community 0 - "Frontend Build Dependencies"
Cohesion: 0.06
Nodes (43): eslint, @eslint/js, eslint-plugin-react-hooks, eslint-plugin-react-refresh, globals, react-dom, tailwindcss, @tailwindcss/vite (+35 more)

### Community 2 - "Agent Guardrail Tests"
Cohesion: 0.13
Nodes (10): check_refusal(), remove_all_punctuation(), send_user_utterance(), test_agent_answers_question(), test_agent_comprehensive_guardrails(), test_agent_critical_guardrails_only(), test_agent_photobooth_workflow(), tool_state_checker() (+2 more)

### Community 3 - "procedural_clips.py"
Cohesion: 0.10
Nodes (4): Animation, AnimationClip, ProceduralAnimation, StaticAnimation

### Community 4 - "PhotoGate"
Cohesion: 0.24
Nodes (4): fresh_frame(), detection(), GateTests, PhotoGate

### Community 6 - "Tracker Detection Pipeline"
Cohesion: 0.08
Nodes (3): TrackerService, DetectionResult, Config

### Community 9 - "TTS Kokoro Engine"
Cohesion: 0.11
Nodes (3): TextToSpeechService, BaseTTSModel, KokoroTTSModel

### Community 10 - "STT Riva Client"
Cohesion: 0.10
Nodes (8): AudioConfig, EndpointingConfig, RivaConfig, Seconds, SpeechToTextConfig, VadConfig, SpeechToTextService, PausableRivaMicrophoneStream

### Community 11 - "Photo Booth State Machine"
Cohesion: 0.10
Nodes (3): PhotoBoothBotStateMachine, finding_user_sequence(), States

### Community 12 - "LLM Tool Abstraction"
Cohesion: 0.11
Nodes (4): create_tool_from_basetool(), UnifiedLLM, convert_message_to_dict(), BaseMessage

### Community 13 - "filters.py"
Cohesion: 0.07
Nodes (7): AdaptiveFilter, BaseLowPassFilter, ButterworthFilter, create_filter(), ExponentialMovingAverageFilter, FilterMethod, KalmanFilter

### Community 14 - "subscribe"
Cohesion: 0.07
Nodes (6): UiServerService, produces(), decorator(), wrapper(), subscribe(), decorator()

### Community 15 - "litellm.py"
Cohesion: 0.08
Nodes (6): completion_client_langchain(), completion_client_provider(), CompletionClientConfig, create_tool_from_callable(), ToolCall, ToolParameter

### Community 16 - "Procedural Audio Effects"
Cohesion: 0.11
Nodes (5): AudioEffect, BitCrushEffect, PitchBendEffect, StutterEffect, WobbleEffect

### Community 17 - "Robot Position Debug Plots"
Cohesion: 0.11
Nodes (8): load_position_data(), main(), plot_positions(), plot_velocities(), save_highest_velocities(), main(), play_positions(), read_positions_from_csv()

### Community 18 - "Image Generation Tool"
Cohesion: 0.10
Nodes (12): _create_external_sharing_urls(), _fetch_and_validate_image(), _generate_download_page_html(), generate_image_tool(), _inner(), _generate_qr_code(), GenerateImageInput, GenerateImageOutput (+4 more)

### Community 19 - "Robot Controller Compose"
Cohesion: 0.05
Nodes (37): condition, UV_FLAGS, args, context, dockerfile, content, configs, config_robot_controller (+29 more)

### Community 20 - "robot-controller-service/src/utils.py"
Cohesion: 0.12
Nodes (5): clip_frame_by_max_delta(), config_respeaker(), frame_to_string(), remap_head_translation(), start_daemon()

### Community 21 - "Frontend App & Messages"
Cohesion: 0.10
Nodes (18): App(), BigMessage(), BigMessageProps, Binoculars(), BinocularsProps, CapturedImage(), Crosshair(), CrosshairProps (+10 more)

### Community 22 - "Agent HITL & MinIO Config"
Cohesion: 0.13
Nodes (7): MinioConfig, look_at_human_tool(), _inner(), LookAtHumanInput, LookAtHumanOutput, LookAtHumanToolConfig, capture_image()

### Community 23 - "tracker-service/src/main.py"
Cohesion: 0.12
Nodes (5): get_format_from_width(), from_cv2_to_torch(), from_torch_to_cv2(), BaseDetector, create_detector()

### Community 24 - "Agent Service Compose"
Cohesion: 0.07
Nodes (29): build, container_name, depends_on, develop, environment, healthcheck, image, restart (+21 more)

### Community 26 - "Easing Curves"
Cohesion: 0.08
Nodes (27): ease_in_bounce(), ease_in_circ(), ease_in_elastic(), ease_in_expo(), ease_in_out_back(), ease_in_out_bounce(), ease_in_out_circ(), ease_in_out_cubic() (+19 more)

### Community 27 - "ConsumerConfig"
Cohesion: 0.17
Nodes (7): listen_only(), main(), wait_for_event(), _wait_for_event(), ConsumerConfig, Consumer, Topic

### Community 28 - "LLM Completion Client"
Cohesion: 0.12
Nodes (3): CompletionClient, LLMResponse, Tool

### Community 29 - "Compositor Audio Devices"
Cohesion: 0.10
Nodes (5): create_animation_frames(), create_robot_message(), find_output_device_index(), validate_audio_settings(), find_device_index()

### Community 30 - "Interaction Event Handling"
Cohesion: 0.10
Nodes (3): UserTrackerStateMachine, Config, States

### Community 31 - "Frequency Generator Effects"
Cohesion: 0.17
Nodes (11): FrequencyGenerator, HarmonicsEffect, PulseEffect, SmoothingEffect, generate_body_angle_sound(), generate_head_pitch_sound(), generate_head_roll_sound(), generate_head_yaw_sound() (+3 more)

### Community 32 - "Compositor Compose"
Cohesion: 0.07
Nodes (27): build, configs, container_name, depends_on, develop, devices, environment, image (+19 more)

### Community 33 - "config.py"
Cohesion: 0.08
Nodes (8): run_mock_service(), consumer_config(), kafka_broker_url(), producer(), pytest_addoption(), TextToSpeechServiceConfig, Robot, OffsetType

### Community 34 - "STT Compose"
Cohesion: 0.07
Nodes (27): context, dockerfile, content, configs, config_speech_to_text, source, target, redpanda (+19 more)

### Community 35 - "Interaction Manager Compose"
Cohesion: 0.07
Nodes (26): condition, context, dockerfile, content, configs, config_interaction_manager, source, target (+18 more)

### Community 36 - "KafkaAsyncCallbackHandler"
Cohesion: 0.12
Nodes (5): KafkaAsyncCallbackHandler, dict_to_protobuf_map(), protobuf_map_to_dict(), protobuf_value_to_python(), python_to_protobuf_value()

### Community 37 - "Robot Light Effects"
Cohesion: 0.17
Nodes (4): LightEffect, LightManager, FillCircleAnimation, StaticAnimation

### Community 38 - "UI Server Runtime"
Cohesion: 0.20
Nodes (10): State, AbortMessage, AppState, AskHuman, BoundingCircle, GenerateImage, GreetUser, LookAtHuman (+2 more)

### Community 39 - "Animation Compositor Service"
Cohesion: 0.12
Nodes (3): BlendingAnimationClip, ProceduralType, AnimationCompositorService

### Community 41 - "Interaction Manager Config"
Cohesion: 0.13
Nodes (8): AnimationConfig, InteractionManagerConfig, LightConfig, PhotoBoothBotConfig, Range, RobotConfig, TrackingConfig, VoiceConfig

### Community 42 - "Animation DB Compose"
Cohesion: 0.08
Nodes (23): build, configs, container_name, depends_on, develop, image, restart, volumes (+15 more)

### Community 43 - "Remote Control Compose"
Cohesion: 0.08
Nodes (23): context, dockerfile, content, configs, config_remote_control, source, target, redpanda (+15 more)

### Community 44 - "ByteTrack Detector"
Cohesion: 0.12
Nodes (3): ByteTrackConfig, ByteTrackDetector, Detectron2Detector

### Community 45 - "UI Server Compose"
Cohesion: 0.08
Nodes (23): context, dockerfile, content, configs, config_ui_server, source, target, redpanda (+15 more)

### Community 47 - "Agent Service Main"
Cohesion: 0.15
Nodes (3): AgentService, single_call(), create_hitl_callback()

### Community 49 - "Service"
Cohesion: 0.22
Nodes (4): BaseMetric, TTSLatencyMetric, TTSRateMetric, Service

### Community 51 - "Architecture Diagram"
Cohesion: 0.11
Nodes (22): Architecture Diagram, Agent (NeMo Agent Toolkit), Animation Compositor, Animation Database, Browser, Camera Service, Camera Device, Image Generator (FLUX.1 Kontext) (+14 more)

### Community 52 - "Frontend TS App Config"
Cohesion: 0.09
Nodes (21): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, jsx, lib, module, moduleDetection, moduleResolution (+13 more)

### Community 56 - "WebRTC Session"
Cohesion: 0.11
Nodes (3): StreamTrack, connect(), Session

### Community 58 - "TTS Compose"
Cohesion: 0.10
Nodes (20): context, dockerfile, redpanda, resources, watch, condition, devices, reservations (+12 more)

### Community 59 - "Tracker Compose"
Cohesion: 0.10
Nodes (20): context, dockerfile, redpanda, resources, watch, condition, devices, reservations (+12 more)

### Community 60 - "Photobooth Workflow Config"
Cohesion: 0.10
Nodes (20): workflow, additional_instructions, allow_null_tool, greet_message, human_feedback_tool, llm_name, max_history, max_retries (+12 more)

### Community 62 - "Camera Compose"
Cohesion: 0.10
Nodes (19): context, dockerfile, build, container_name, depends_on, develop, devices, image (+11 more)

### Community 64 - "Frontend TS Node Config"
Cohesion: 0.10
Nodes (19): compilerOptions, allowImportingTsExtensions, erasableSyntaxOnly, lib, module, moduleDetection, moduleResolution, noEmit (+11 more)

### Community 66 - "react_function.py"
Cohesion: 0.09
Nodes (6): StructuredAgentAction, PhotoBoothReactAgentGraph, photo_booth_react_function(), _response_fn(), _str_api_fn(), StructuredReActGraphState

### Community 69 - "Frontend Compose"
Cohesion: 0.11
Nodes (17): condition, args, context, dockerfile, agent, watch, services, ui (+9 more)

### Community 70 - "animation-database-service/src/main.py"
Cohesion: 0.13
Nodes (3): convert_audio(), LRUCacheDict, DatabaseConfig

### Community 71 - "Remote Control Server"
Cohesion: 0.17
Nodes (4): main(), RemoteControlConfig, RemoteControlService, TriggerCommandRequest

### Community 72 - "Look-At Behaviour"
Cohesion: 0.17
Nodes (4): Degrees, KeyPosition, Position, Robot

### Community 73 - "Frontend API Types"
Cohesion: 0.12
Nodes (15): AbortMessage, Animation, AppState, AskHuman, BaseMessage, BoundingCircle, COLOR, FillCircleAnimation (+7 more)

### Community 74 - "Clip Test Script"
Cohesion: 0.15
Nodes (13): main(), change_volume(), look_at(), play_clip(), play_multiple(), producer_send(), Robot, stop_clip() (+5 more)

### Community 75 - "AsyncTests"
Cohesion: 0.24
Nodes (3): AsyncTests, consume(), load_method()

### Community 76 - "Workspace Packages"
Cohesion: 0.13
Nodes (15): agent, animation-compositor, animation-database, camera, interaction-manager, metrics, photo-booth-agent, remote-control (+7 more)

### Community 77 - "Template Compose"
Cohesion: 0.13
Nodes (14): context, dockerfile, watch, build, container_name, develop, environment, image (+6 more)

### Community 80 - "End Interaction Tool"
Cohesion: 0.14
Nodes (13): end_interaction(), _arun(), EndInteractionInput, EndInteractionToolConfig, hitl_function(), _arun(), HITLFunctionConfig, HITLFunctionInput (+5 more)

### Community 81 - "llm/utils.py"
Cohesion: 0.15
Nodes (6): convert_delta_to_message_chunk(), convert_dict_to_message(), extract_and_parse_json(), get_item_type_schema(), get_parameter_schema(), extract_positions()

### Community 82 - "Audio Debug Docs"
Cohesion: 0.14
Nodes (12): plot_debug_positions.py script, AudioEffect (base class), create_audio_debug_plot() (audio_debug), DistortionEffect, easing_curves module, EchoEffect, FrequencyGenerator, HarmonicsEffect (+4 more)

### Community 83 - "Remote Control Events"
Cohesion: 0.15
Nodes (14): End Event, Listen Event, Start Event, Think Event, UserAppeared Event, UserDisappeared Event, WakeUp Event, Remote Control Output Log Area (+6 more)

### Community 84 - "service.py"
Cohesion: 0.16
Nodes (5): MetricsServiceConfig, MyServiceConfig, UiServerConfig, BaseConfig, ProducerConfig

### Community 85 - "Metrics Compose"
Cohesion: 0.14
Nodes (13): context, dockerfile, watch, build, container_name, develop, image, restart (+5 more)

### Community 86 - "Pixelated Image Hook"
Cohesion: 0.23
Nodes (9): react, canvasDimensions, usePixelatedImage(), ImageGeneration(), ImageGenerationProps, TEXTS, TextCarousel(), TextCarouselProps (+1 more)

### Community 87 - "Agent & Camera Docs"
Cohesion: 0.19
Nodes (12): Agent Service, mock_user.py script, Photo Booth Assistant config (photobooth.yml), trigger_agent_restart.py script, Procedural Animation Generation (look_at, tracking), test_clips.py script, camera_serial_or_url config, Camera Service (+4 more)

### Community 88 - "animations.py"
Cohesion: 0.11
Nodes (6): blend_multiple_frames(), Degrees, EulerAngles, interpolate(), lerp(), slerp()

### Community 89 - "Compositor Audio Config"
Cohesion: 0.18
Nodes (3): AudioConfig, CompositorConfig, Robot

### Community 90 - "Animation Data Model"
Cohesion: 0.21
Nodes (4): Animation, AnimationData, JointData1D, JointData2D

### Community 91 - "GPU Deploy Resources"
Cohesion: 0.15
Nodes (13): resources, deploy, deploy, devices, reservations, container_name, deploy, environment (+5 more)

### Community 92 - "MinIO Infrastructure"
Cohesion: 0.15
Nodes (13): MINIO_ROOT_PASSWORD, MINIO_ROOT_USER, interval, retries, timeout, command, container_name, environment (+5 more)

### Community 93 - "Getting Started Docs"
Cohesion: 0.23
Nodes (13): Getting Started Guide, OpenTelemetry endpoints (lgtm-otel:4317/4318), VS Code container debugging (service-debug.override.yaml), .env config (NVIDIA_API_KEY, HF_TOKEN), FLUX.1-Kontext-dev model (non-commercial), Flux.1-Kontext NIM container (nvcr.io), gpt-oss-20b model, Grafana OTEL LGTM stack (+5 more)

### Community 94 - "Redpanda & Remote Control Docs"
Cohesion: 0.18
Nodes (13): Redpanda (Kafka broker), Remote Control Service README, remote_control_command_topic (RemoteControlCommand), Remote Control Web UI (index.html), POST /api/trigger-command, Service Template README, Integration Tests README, MessageListener (+5 more)

### Community 95 - "Capture & Countdown UI"
Cohesion: 0.17
Nodes (8): classnames, CapturedImageProps, Countdown(), CountdownProps, FloatingImages(), Sleeping(), VideoFeed(), VideoFeedProps

### Community 96 - "Animated Border UI"
Cohesion: 0.27
Nodes (7): FillCircleBorder(), FillCircleBorderProps, LightBorder(), LightBorderProps, AnimationProps, COLORS, StaticBorder()

### Community 98 - "UI Server Status Models"
Cohesion: 0.18
Nodes (3): clear_task(), clear_task(), update_callback()

### Community 99 - "LLM Params Config"
Cohesion: 0.17
Nodes (12): allowed_openai_params, reasoning_effort, additional_kwargs, api_key, base_url, max_retries, max_tokens, model_name (+4 more)

### Community 100 - "Agent Exceptions"
Cohesion: 0.23
Nodes (3): InvalidImageError, NoResponseError, SuggestionMessage

### Community 101 - "animation-database-service/src/utils.py"
Cohesion: 0.29
Nodes (4): convert_bits_per_sample(), Degrees, EulerAngle, TrackingData

### Community 102 - "Redpanda Console Config"
Cohesion: 0.17
Nodes (12): CONFIG_FILEPATH, CONSOLE_CONFIG_FILE, command, container_name, depends_on, entrypoint, environment, image (+4 more)

### Community 103 - "Hardware & Model Overview"
Cohesion: 0.20
Nodes (9): Reachy USB/power setup and speaker_setup.sh, NVIDIA DGX Spark, Kokoro-82M TTS model, Reachy Mini robot, Spark & Reachy Photo Booth overview, Troubleshooting Guide, Parakeet 1.1b CTC ASR NIM, Spark & Reachy Mini Playbook (+1 more)

### Community 105 - "Interaction & Robot Docs"
Cohesion: 0.17
Nodes (11): Interaction Manager Service README, Interaction Manager, Robot Utterances (robot_utterances.yaml), Room Mapping Coordinate System, Tool Names Categories (start/human/image_generation/taking_picture/end), Robot Controller Service README, reachy_config (use_sim, media_backend), Reachy Mini Robot (+3 more)

### Community 106 - "Photo Capture Flow Docs"
Cohesion: 0.20
Nodes (11): Agent Service (LLM-powered), Camera /capture endpoint frame-index check, center_user_timeout, workmesh.photo_gate.PhotoGate, Tracker Service README, ByteTrack Multi-Person Tracking, COCO 17 Keypoints Convention, Detection Smoothing (EMA/Butterworth/Kalman/Adaptive) (+3 more)

### Community 107 - "Speech & Latency Docs"
Cohesion: 0.18
Nodes (11): e2e.latency histogram, user_utterance_topic (UserUtterance), ReSpeaker XVF3800 4-Mic Array, udev rules 99-reachy-mini.rules, speaker_setup.sh script, Speech-to-Text Service README, input_device_index_or_name / audio_config.sample_rate, list_sound_devices.py (+3 more)

### Community 109 - "Kiosk Frontend Docs"
Cohesion: 0.20
Nodes (9): ui-frontend AGENTS.md (Cursor Rules), FloatingImages component, React 19 / Vite 7 / Tailwind CSS 4 / TypeScript, ui-frontend index.html (Vite entry), Spark & Reachy Photo Booth UI README, UI Server WebRTC test page (index.html), WebRTC Signalling over WebSocket (/ws), UI Server Service README (+1 more)

### Community 110 - "robot-controller-service/src/configuration.py"
Cohesion: 0.09
Nodes (3): ReachyConfig, RespeakerConfig, Robot

### Community 111 - "DetectionFilter"
Cohesion: 0.10
Nodes (4): compute_box_center_distance(), compute_iou(), DetectionFilter, TrackFilters

### Community 113 - "Compose Config Mounts"
Cohesion: 0.22
Nodes (11): source, target, configs, container_name, image, ports, restart, volumes (+3 more)

### Community 114 - "Volume Init Container"
Cohesion: 0.18
Nodes (11): init-volumes, container_name, depends_on, environment, image, ports, restart, volumes (+3 more)

### Community 115 - "Robot Utterances Data"
Cohesion: 0.18
Nodes (10): demo_information, facts, performance, generate_image, completed, look_at_human, completed, started (+2 more)

### Community 117 - "Guardrails Dataset"
Cohesion: 0.21
Nodes (5): check_deflection(), get_critical_test_cases(), get_test_cases_by_category(), get_test_cases_by_severity(), GuardrailTestCase

### Community 119 - "Agent Prompt Config"
Cohesion: 0.20
Nodes (10): prompt, _type, _type, functions, ask_human, farewell_user, greet_user, look_at_human (+2 more)

### Community 120 - "Producer"
Cohesion: 0.13
Nodes (8): producer_send(), play_clip_async(), producer_send(), restart_agent(), test_tts_generates_audio_from_text(), test_tts_handles_multiple_requests(), producer_send(), Producer

### Community 122 - "Shared Volumes"
Cohesion: 0.20
Nodes (10): volumes, cache, grafana, hf, loki, minio, nim, phoenix_data (+2 more)

### Community 123 - "Photobooth Root Config"
Cohesion: 0.22
Nodes (8): general, telemetry, llms, endpoint, project, _type, tracing, phoenix

### Community 124 - "Agent MinIO Settings"
Cohesion: 0.22
Nodes (9): access_key, base_url, bucket, create_bucket, image_base_url, internal_base_url, secret_key, secure (+1 more)

### Community 125 - "Shared Sample Rate Docs"
Cohesion: 0.31
Nodes (8): Animation Compositor Service, audio_config (output_device_index_or_name, sample_rate), list_sound_devices.py script, Animation Database Service, Blender Animation Library (assets/animLibrary), Procedural Audio Generation (motor sounds), test_procedural_audio.py script, Reachy speaker device conflict (Error querying device -1)

### Community 126 - "ServiceExecutor"
Cohesion: 0.13
Nodes (14): main(), main(), main(), main(), main(), main(), main(), main() (+6 more)

### Community 127 - "Root Compose Includes"
Cohesion: 0.22
Nodes (8): include, command, container_name, image, restart, volumes, services, init-volumes

### Community 128 - "Infra Service Commands"
Cohesion: 0.22
Nodes (9): command, container_name, environment, image, ipc, ports, restart, volumes (+1 more)

### Community 129 - "TTS Docs"
Cohesion: 0.25
Nodes (8): talkingForward Speech Animation, clip_data_topic (ClipData), Text-to-Speech Service README, Animation Compositor, cache_kokoro_model_and_voices.py, KittenTTS / Kokoro TTS models, Kafka max.message.bytes, Text-to-Speech Service

### Community 132 - "Development Guide"
Cohesion: 0.32
Nodes (7): src/configuration.py defaults overridden by compose.yaml, Development Guide, Hot Reload (docker compose --watch), Deployment Instructions, Web UI (http://127.0.0.1:3001), Service template scaffolding (template/), Writing Your First Service tutorial

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

### Community 148 - "Metrics Docs"
Cohesion: 0.33
Nodes (7): Metrics Service README, workmesh.config.BaseConfig / load_config, human_speech_request_topic (HumanSpeechRequest), LGTM OpenTelemetry Collector (Grafana), Metrics Service, tts.latency histogram, tts.rate histogram

### Community 149 - "ReAct Agent Docs"
Cohesion: 0.40
Nodes (4): Agent State (messages + agent_scratchpad), PhotoBoothReactWorkflowConfig, Tool call Kafka events (TOOL_CALL_STARTED/COMPLETED/FAILED), NeMo Agent Toolkit

### Community 153 - "Workmesh Framework Docs"
Cohesion: 0.33
Nodes (5): Workmesh framework, ping_topic / Ping protobuf message, workmesh Service base class, ServiceExecutor, @subscribe decorator

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

### Community 158 - "AudioMixer"
Cohesion: 0.10
Nodes (3): AudioMixer, BaseClip, StaticClip

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
Cohesion: 0.67
Nodes (4): GET /api/commands, loadCommands(), setupKeyboardShortcuts(), triggerCommand()

### Community 175 - "MinIO QR Sharing"
Cohesion: 1.00
Nodes (3): EXTERNAL_MINIO_BASE_URL env var, QR-code sharing on local network, MinIO object storage

### Community 193 - "camera-service/src/configuration.py"
Cohesion: 0.24
Nodes (3): ImageEncoding, Resolution, Robot

### Community 194 - "parse_tool_calls"
Cohesion: 0.24
Nodes (6): multi_tool_completion_checker(), condition(), parse_tool_calls(), condition(), tool_transition_checker(), condition()

### Community 197 - "trigger_tts.py"
Cohesion: 0.36
Nodes (3): main(), producer_send(), Robot

### Community 199 - "Connecting applications to the wireless Reachy"
Cohesion: 0.25
Nodes (7): 1. Network requirements, 2. Configure the bridge, 3. Start and verify, 4. Call the bridge from your application, 5. Connecting from the Hermes (OpenShell) sandbox, 6. Troubleshooting, Connecting applications to the wireless Reachy

## Ambiguous Edges - Review These
- `Image Generator (FLUX.1 Kontext)` → `MinIO`  [AMBIGUOUS]
  docs/images/architecture-diagram.png · relation: shares_data_with
- `Workmesh Messaging Library` → `Service Template README`  [AMBIGUOUS]
  template/README.md · relation: conceptually_related_to

## Knowledge Gaps
- **85 isolated node(s):** `spark-reachy-photo-booth`, `animation-compositor`, `animation-database`, `camera`, `interaction-manager` (+80 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 1439 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **71 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Service` connect `Service` to `Tracker Detection Pipeline`, `TTS Kokoro Engine`, `STT Riva Client`, `subscribe`, `ConsumerConfig`, `Animation Compositor Service`, `Agent Service Main`, `Interaction Manager Service`, `AnimationDatabaseService`, `Camera Service Handler`, `State Enter Handlers`, `E2E Latency Metric`, `Service Template`, `ui-server-service/src/main.py`, `.stop`, `Remote Control Server`, `Robot Controller Shutdown`, `service.py`, `Service Telemetry`, `Producer`, `Workmesh Service Runtime`, `ServiceExecutor`?**
  _High betweenness centrality (0.045) - this node is a cross-community bridge._
- **Are the 6 inferred relationships involving `PhotoBoothBotStateMachine` (e.g. with `InteractionManagerService` and `LightEffect`) actually correct?**
  _`PhotoBoothBotStateMachine` has 6 INFERRED edges - model-reasoned connections that need verification._
- **What connects `spark-reachy-photo-booth`, `animation-compositor`, `animation-database` to the rest of the system?**
  _85 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `Frontend Build Dependencies` be split into smaller, more focused modules?**
  _Cohesion score 0.0647342995169082 - nodes in this community are weakly interconnected._
- **Why does `PhotoBoothBotStateMachine` connect `Photo Booth State Machine` to `State Enter Handlers`, `PhotoGate`, `Robot Light Effects`, `Photo Preparation Gate`, `Robot Utterance Manager`, `Look-At Behaviour`, `Interaction Manager Service`, `User Utterance Handling`, `enter_state`, `State Exit Handlers`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._

### Low-confidence Hints
_AMBIGUOUS edges — the extractor was unsure. Verify before acting on these._

- **What is the exact relationship between `Image Generator (FLUX.1 Kontext)` and `MinIO`?**
  _Edge tagged AMBIGUOUS (relation: shares_data_with) - confidence is low._
- **What is the exact relationship between `Workmesh Messaging Library` and `Service Template README`?**
  _Edge tagged AMBIGUOUS (relation: conceptually_related_to) - confidence is low._