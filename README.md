# 🌱 AgroConnect – A Smart Agricultural Marketplace  

AgroConnect is a digital platform that **empowers farmers** and **connects them with buyers** worldwide. With an intuitive UI, **secure transactions**, **real-time chat**, and **AI-powered insights**, it **revolutionizes** the agricultural trading experience.  

## 🚀 Key Features  

### 🌍 **User-Friendly Marketplace**  
- Clean, modern, and **responsive UI** for effortless navigation.  
- **Interactive product listings** with images, descriptions, and price updates.  

### 🔄 **Real-Time Notifications & Chatting**  
- **Instant notifications** for new listings, offers, and transactions.  
- **WebSocket-based real-time chat** for seamless buyer-seller communication.  
- **Google Translate API integration** for automatic language translation in chat.  

### 🔐 **Secure Transactions**  
- **Razorpay API** integration for **seamless payments** via UPI, cards, and net banking.  
- **Escrow-based payment system** (Upcoming).  

### 📜 **Smart Contract Management**  
- **Digitized agreements** for transparent and verified deals.  

### 🤖 **AI-Powered Insights**  
- **Predictive pricing** suggestions based on market trends.  
- **Demand-supply analytics** for strategic decision-making.  

### 📊 **Streamlit-Based Analytics Dashboard**  
- Farmers and buyers can **view real-time insights** on pricing and trends.  

### 💾 **SQL Database for Secure Storage**  
- **MySQL ensures efficient, scalable, and **secure** data management.  

---

## 🏗 **Project Structure**  

```
agroconnect/
│
├── app.py                  # 🎯 Main application file
├── config.py               # ⚙️ Configuration variables
├── database.py             # 💾 Database operations
├── auth.py                 # 🔐 Authentication functions
├── marketplace.py          # 🛒 Marketplace functionality
├── payment.py              # 💳 Payment integration
├── translator.py           # 🌍 Translation services
├── chat.py                 # 💬 Real-time chat functionality
├── utils.py                # 🔧 Utility functions
│
├── assets/                 # 🎨 Static assets
│   ├── css/                # 🎨 CSS files
│   ├── images/             # 🖼 Image files
│   └── js/                 # 📜 JavaScript files
│
├── data/                   # 📂 Data storage
│   └── agroconnect.db      # 🗄 MySQL database
│
└── requirements.txt        # 📌 Project dependencies
```

---

## 🔗 **Project Links**  

- **Live Deployment:** [Here](https://agroconnect.streamlit.app/)
  
---

## 🛠 **Tech Stack Used**  

| Component         | Tech Used |
|------------------|-----------|
| 🖥 **Frontend**  | Streamlit, Tailwind CSS |
| ⚡ **Backend**   | FastAPI, WebSocket |
| 💾 **Database**  | MySQL |
| 💰 **Payments**  | Razorpay API |
| 🌍 **Translation** | Google Translate API |
| 🔐 **Authentication** | OAuth |
| 🚀 **Hosting** | Streamlit Cloud |

---

## 🛠 **How to Set Up the Project?**  

1️⃣ **Clone the repository:**  
```bash
git clone https://github.com/Anidipta/AgroConnect.git
cd AgroConnect
```

2️⃣ **Install dependencies:**  
```bash
pip install -r requirements.txt
```

3️⃣ **Run the application:**  
```bash
streamlit run app.py
```

---

## 🔥 **Future Enhancements**  
✅ **AI-powered recommendations** for pricing.   
✅ **Machine Learning models** for demand forecasting.  

🚀 **AgroConnect is the future of agriculture trading!**  
