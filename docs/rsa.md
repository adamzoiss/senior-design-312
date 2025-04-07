# RSA Encryption and Decryption

## RSA Overview

RSA (Rivest-Shamir-Adleman) is an asymmetric encryption algorithm that uses a pair of keys: a public key for encryption and a private key for decryption. This allows secure communication without having to share a secret key beforehand.

## Simplified RSA Process

```mermaid
%%{init: {'theme': 'default', 'themeVariables': { 'fontSize': '18px', 'fontFamily': 'arial', 'edgeLabelBackground':'#ffffff', 'tertiaryColor': '#f5f5f5'}, 'flowchart': {'diagramPadding': 40, 'curve': 'linear'}} }%%
graph TB
    %% Define styles
    classDef plaintext fill:#d4f1f9,stroke:#0e5f8a,stroke-width:2px
    classDef keys fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef process fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef ciphertext fill:#f8cecc,stroke:#b85450,stroke-width:2px

    %% Key generation
    KG[Key Generation]
    PK[Public Key]
    SK[Private Key]
    KG --> PK
    KG --> SK

    %% Encryption flow
    P[Plaintext Message] --> E[Mathematical Operation]
    PK --> E
    E --> C[Ciphertext]

    %% Decryption flow
    C --> D[Mathematical Operation]
    SK --> D
    D --> P2[Plaintext Message]

    %% Apply styles
    class P,P2 plaintext
    class PK,SK keys
    class KG,E,D process
    class C ciphertext
```

## Key Components of RSA

1. **Key Generation**: The creation of a mathematically linked public and private key pair
2. **Public Key**: Shared openly and used to encrypt messages
3. **Private Key**: Kept secret and used to decrypt messages
4. **Mathematical Operations**: Based on the difficulty of factoring large prime numbers
5. **Modular Arithmetic**: Mathematical operations performed with remainders

## RSA Key Generation

```mermaid
flowchart TB
    %% Define styles
    classDef operand fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef operation fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef result fill:#f8cecc,stroke:#b85450,stroke-width:2px

    %% Key generation steps
    P1[Choose large prime p] --> M[Multiply]
    P2[Choose large prime q] --> M
    M --> N[n = p × q]

    P1 --> C1["Calculate (p-1)"]
    P2 --> C2["Calculate (q-1)"]
    C1 --> T[Multiply]
    C2 --> T
    T --> PHI["φ(n) = (p-1)(q-1)"]

    PHI --> CE["Choose e"]
    CE --> E["Public exponent e\n(relatively prime to φ(n))"]

    PHI --> CD["Calculate d"]
    E --> CD
    CD --> D["Private exponent d\n(d × e ≡ 1 mod φ(n))"]

    N --> PUB["Public Key (e, n)"]
    E --> PUB

    N --> PRIV["Private Key (d, n)"]
    D --> PRIV

    %% Apply styles
    class P1,P2,PHI,E,D operand
    class M,C1,C2,T,CE,CD operation
    class N,PUB,PRIV result
```

## RSA in Action

```mermaid
graph LR
    %% Define styles
    classDef plaintext fill:#d4f1f9,stroke:#0e5f8a,stroke-width:2px
    classDef key fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef process fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef ciphertext fill:#f8cecc,stroke:#b85450,stroke-width:2px

    %% Encryption process
    subgraph Encryption
        M[Message M] --> E["Encrypt: C = M^e mod n"]
        PK["Public Key (e, n)"] --> E
        E --> C[Ciphertext C]
    end

    %% Decryption process
    subgraph Decryption
        C2[Ciphertext C] --> D["Decrypt: M = C^d mod n"]
        SK["Private Key (d, n)"] --> D
        D --> M2[Message M]
    end

    %% Apply styles
    class M,M2 plaintext
    class PK,SK key
    class E,D process
    class C,C2 ciphertext
```

## Advantages and Limitations of RSA

### Advantages

- **No Shared Secret**: Communicating parties don't need to share a secret key in advance
- **Digital Signatures**: Can be used to verify the sender's identity
- **Key Distribution**: Simplifies secure key exchange over insecure channels

### Limitations

- **Performance**: Significantly slower than symmetric encryption like AES
- **Key Size**: Requires large keys (2048+ bits) for security
- **Data Size**: Limited to encrypting data smaller than the key size
- **Quantum Vulnerability**: Vulnerable to quantum computing attacks

## Hybrid Encryption

Due to RSA's performance limitations, it's often used in a hybrid approach with symmetric encryption:

```mermaid
graph TD
    %% Define styles
    classDef plaintext fill:#d4f1f9,stroke:#0e5f8a,stroke-width:2px
    classDef key fill:#ffe6cc,stroke:#d79b00,stroke-width:2px
    classDef process fill:#d5e8d4,stroke:#82b366,stroke-width:2px
    classDef ciphertext fill:#f8cecc,stroke:#b85450,stroke-width:2px

    %% Encryption flow
    M[Message] --> AE[AES Encryption]
    AK[Random AES Key] --> AE
    AE --> C[Encrypted Message]

    AK --> RE[RSA Encryption]
    PK[RSA Public Key] --> RE
    RE --> EK[Encrypted AES Key]

    %% Decryption flow
    EK --> RD[RSA Decryption]
    SK[RSA Private Key] --> RD
    RD --> AK2[AES Key]

    C --> AD[AES Decryption]
    AK2 --> AD
    AD --> M2[Original Message]

    %% Apply styles
    class M,M2,AK,AK2 plaintext
    class PK,SK key
    class AE,RE,RD,AD process
    class C,EK ciphertext
```

This hybrid approach provides:

- The security of RSA for key exchange
- The performance of AES for data encryption
- The ability to encrypt data of any size efficiently
