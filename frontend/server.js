// server.js

const express = require('express');
const path = require('path');
const cors = require('cors');



const app = express();
app.use(cors());

// 모든 OPTIONS 요청에 대한 응답 설정
app.options('*', cors());
const PORT = 3336;  // 서버가 실행될 포트

// 정적 파일(HTML, CSS, JS) 제공 설정
app.use(express.static('public'));

// 서버 시작
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});
