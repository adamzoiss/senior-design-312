```mermaid
classDiagram
    class ThreadManager {
        "Manages threads and their lifecycle."
    }

    class CryptoManager {
        "Handles encryption and decryption."
    }

    class BaseAudioManager {
        "Manages audio input/output and encryption."
    }

    class AudioManager {
        "Extends BaseAudioManager with additional audio features."
    }
    AudioManager

    class GPIOHandler {
        "Handles GPIO setup and alerts."
    }

    class DisplayHandler {
        "Manages display navigation and rendering."
    }

    class RFManager {
        "Handles RF communication and audio streaming."
    }

    class InterfaceManager {
        "Integrates and manages all components for user interaction."
    }
    InterfaceManager --|> GPIOHandler

    %% Interaction Diagram
    BaseAudioManager --> ThreadManager : uses for thread management
    BaseAudioManager --> CryptoManager : uses for encryption
    AudioManager --> BaseAudioManager : extends functionality
    RFManager --> ThreadManager : uses for thread management
    RFManager --> BaseAudioManager : uses for audio streaming
    GPIOHandler --> RFManager : provides GPIO alerts
    DisplayHandler --> ThreadManager : uses for thread management
    InterfaceManager --> DisplayHandler : manages display
    InterfaceManager --> AudioManager : manages audio
    InterfaceManager --> RFManager : manages RF communication
    InterfaceManager --> ThreadManager : uses for thread management
```