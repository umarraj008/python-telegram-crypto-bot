# Changelog

All notable changes to this project are listed below.

**[v3.2.1-alpha]**
- Fixed issue with deleted messages not getting forwarded to private channel

**[v3.2-alpha]**
- Integrated bot logging to private channel 

**[v3.1-alpha]**
- Fixed username detection bug
- Created Logger bot
- Created Builder script

**[v3-alpha]**
- Integrated bot controller

**[v2.3]**
- Fixed group chat bug
- Updated split CA detection

**[v2.2]**
- Added support for **private groups** and **channels**
- Now using **dynamic list** to only allow messages from **select users**

**[v2.1]**
- Support for **Solana coin addresses (CA)** with **43-character length**
- Integrated group chat monitoring for **cryptoyeezus**

**[v2.0]**
- **Rug pull detection** improvements
- Detection of **SPLIT CA**
- Detection of the **KING** keyword
- **Solana coin validation** using **Base58 decoding**
- **Length validation** for **Solana addresses** (**44 characters**)
- **Debug output** with **timestamp printing**
- **Rug pull CA** are now saved properly

**[v1.2]**
- Initial **rug pull detection**
- **Word detection** and **removal functionality**

**[v1.0]**
- Monitoring of **Telegram channels**
- Detection of **coin addresses (CA)**
- Forwarding detected **CA** to **trojan bot**