# AES Encryption and Decryption

## AES-256 Overview

AES (Advanced Encryption Standard) is a symmetric encryption algorithm that uses the same key for both encryption and decryption. AES-256 refers to the use of a 256-bit key size, which is currently considered secure against brute force attacks.

## Simplified AES-256 Process

```mermaid
%%{init: {'theme': 'default', 'themeVariables': { 'fontSize': '18px', 'fontFamily': 'arial', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f5f5f5'}, 'flowchart': {'diagramPadding': 40, 'curve': 'linear'}} }%%
graph TB
    %% Define styles
    classDef plaintext fill:#d4f1f9,stroke:#0e5f8a,stroke-width:2px
    classDef key fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef process fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef ciphertext fill:#f8cecc,stroke:#b85450,stroke-width:2px

    %% Simplified encryption flow
    P[Plaintext] --> KE[Key Expansion]
    SK[Secret Key 256 bits] --> KE
    P --> BM[Bit Manipulation 14 Rounds]
    KE --> BM
    BM --> C[Ciphertext]

    %% Simplified decryption flow
    C --> RBM[Reverse Bit Manipulation 14 Rounds]
    KE --> RBM
    RBM --> P2[Plaintext]

    %% Apply styles
    class P,P2 plaintext
    class SK key
    class KE,BM,RBM process
    class C ciphertext
```

## Key Components of AES-256

1. **Secret Key**: A 256-bit (32-byte) key used for both encryption and decryption
2. **Key Expansion**: Process that derives multiple round keys from the original secret key
3. **Bit Manipulation**: AES-256 uses 14 rounds of complex bit operations including:
   - Byte substitution
   - Row shifting
   - Column mixing
   - Key addition

## CFB Mode (Cipher Feedback)

In our implementation, we use AES in CFB (Cipher Feedback) mode, which turns the block cipher into a stream cipher, making it ideal for encrypting continuous data streams like audio.

```mermaid
graph LR
    %% Define styles
    classDef plaintext fill:#d4f1f9,stroke:#0e5f8a,stroke-width:2px
    classDef key fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef process fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef ciphertext fill:#f8cecc,stroke:#b85450,stroke-width:2px
    classDef iv fill:#e1d5e7,stroke:#9673a6,stroke-width:2px

    %% Simplified Encryption
    subgraph Encryption
        IV1[Initialization Vector] --> E1[AES-256 Bit Manipulation]
        K1[Secret Key] --> E1
        E1 --> EO1[Encrypted Output]
        P1[Plaintext Block 1] --> XOR1((XOR))
        EO1 --> XOR1
        XOR1 --> C1[Ciphertext Block 1]

        C1 -->|Feedback| E2[AES-256 Bit Manipulation]
        K1 --> E2
        E2 --> EO2[Encrypted Output]
        P2[Plaintext Block 2] --> XOR2((XOR))
        EO2 --> XOR2
        XOR2 --> C2[Ciphertext Block 2]
    end

    %% Simplified Decryption
    subgraph Decryption
        IV2[Initialization Vector] --> E3[AES-256 Bit Manipulation]
        K2[Secret Key] --> E3
        E3 --> EO3[Encrypted Output]
        C3[Ciphertext Block 1] --> XOR3((XOR))
        EO3 --> XOR3
        XOR3 --> P3[Plaintext Block 1]

        C3 -->|Feedback| E4[AES-256 Bit Manipulation]
        K2 --> E4
        E4 --> EO4[Encrypted Output]
        C4[Ciphertext Block 2] --> XOR4((XOR))
        EO4 --> XOR4
        XOR4 --> P4[Plaintext Block 2]
    end

    %% Apply styles
    class IV1,IV2 iv
    class K1,K2 key
    class P1,P2,P3,P4 plaintext
    class E1,E2,E3,E4,EO1,EO2,EO3,EO4,XOR1,XOR2,XOR3,XOR4 process
    class C1,C2,C3,C4 ciphertext
```

## Advantages for Audio Encryption

- **Stream-based**: Can encrypt data of arbitrary length without padding
- **Partial Block Processing**: Efficient for real-time audio processing
- **Error Propagation**: Limited to one block, minimizing impact on audio quality
- **No Padding Required**: Simplifies the processing pipeline for continuous audio streams
