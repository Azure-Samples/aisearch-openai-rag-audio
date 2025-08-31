from aiohttp import web
import json
import os
import logging

# إعداد التسجيل
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def index(request):
    """صفحة رئيسية بسيطة"""
    html = """
    <!DOCTYPE html>
    <html lang="ar" dir="rtl">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>اختبار التسلسل الصوتي</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
                padding: 20px;
                min-height: 100vh;
                display: flex;
                align-items: center;
                justify-content: center;
                direction: rtl;
            }
            .container {
                background: white;
                padding: 40px;
                border-radius: 20px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.2);
                text-align: center;
                max-width: 500px;
                width: 100%;
            }
            h1 {
                color: #333;
                margin-bottom: 30px;
                font-size: 2.5em;
            }
            .button {
                background: linear-gradient(45deg, #667eea, #764ba2);
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 18px;
                border-radius: 50px;
                cursor: pointer;
                transition: all 0.3s ease;
                margin: 10px;
                min-width: 200px;
            }
            .button:hover {
                transform: translateY(-2px);
                box-shadow: 0 5px 15px rgba(0,0,0,0.2);
            }
            .button:disabled {
                background: #ccc;
                cursor: not-allowed;
                transform: none;
                box-shadow: none;
            }
            .status {
                margin-top: 30px;
                padding: 15px;
                border-radius: 10px;
                font-size: 16px;
                min-height: 20px;
            }
            .status.idle {
                background: #e8f5e8;
                color: #2d5a2d;
            }
            .status.playing {
                background: #fff3cd;
                color: #856404;
            }
            .status.recording {
                background: #f8d7da;
                color: #721c24;
            }
            .status.realtime {
                background: #d1ecf1;
                color: #0c5460;
            }
            .mic-indicator {
                margin-top: 20px;
                padding: 10px;
                border-radius: 10px;
                background: #f8f9fa;
                border: 2px solid #dee2e6;
                display: none;
            }
            .mic-indicator.active {
                display: block;
                border-color: #28a745;
                background: #d4edda;
            }
            .volume-bar {
                width: 100%;
                height: 20px;
                background: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin-top: 10px;
            }
            .volume-level {
                height: 100%;
                background: linear-gradient(90deg, #28a745, #ffc107, #dc3545);
                transition: width 0.1s ease;
                width: 0%;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🎵 اختبار التسلسل الصوتي</h1>
            
            <button id="connectBtn" class="button" onclick="startSequence()">
                🔗 اتصال
            </button>
            
            <button id="stopBtn" class="button" onclick="stopSequence()" disabled>
                ⏹️ إيقاف
            </button>
            
            <div id="status" class="status idle">
                جاهز للاختبار
            </div>
            
            <div id="micIndicator" class="mic-indicator">
                🎤 المايك نشط - مستوى الصوت:
                <div class="volume-bar">
                    <div id="volumeLevel" class="volume-level"></div>
                </div>
            </div>
        </div>

        <script>
            let isSequenceActive = false;
            let currentAudio = null;
            let websocket = null;
            let audioContext = null;
            let analyzer = null;
            let volumeCheckInterval = null;
            let mediaRecorder = null;
            let audioChunks = [];
            
            function updateStatus(message, type = 'idle') {
                const status = document.getElementById('status');
                status.textContent = message;
                status.className = 'status ' + type;
            }
            
            function updateButtons(sequenceActive) {
                const connectBtn = document.getElementById('connectBtn');
                const stopBtn = document.getElementById('stopBtn');
                
                connectBtn.disabled = sequenceActive;
                stopBtn.disabled = !sequenceActive;
                
                isSequenceActive = sequenceActive;
            }
            
            async function playAudioFile(url) {
                return new Promise((resolve, reject) => {
                    currentAudio = new Audio(url);
                    
                    currentAudio.addEventListener('ended', () => {
                        resolve();
                    });
                    
                    currentAudio.addEventListener('error', (e) => {
                        console.error('Audio error:', e);
                        reject(e);
                    });
                    
                    currentAudio.play().catch(reject);
                });
            }
            
            async function startSequence() {
                if (isSequenceActive) return;
                
                updateButtons(true);
                
                try {
                    // 1. تشغيل ملف Ran.mp3 (الرنة)
                    updateStatus('🔔 يتم تشغيل نغمة الرنين...', 'playing');
                    await playAudioFile('/static/audio/Ran.mp3');
                    
                    // انتظار قصير
                    await new Promise(resolve => setTimeout(resolve, 500));
                    
                    // 2. تشغيل ملف between.wav
                    updateStatus('🗣️ يتم تشغيل الرسالة الأولى...', 'playing');
                    await playAudioFile('/static/audio/between.wav');
                    
                    // انتظار قصير
                    await new Promise(resolve => setTimeout(resolve, 500));
                    
                    // 3. تشغيل ملف Nancy.wav
                    updateStatus('👩 يتم تشغيل رسالة Nancy...', 'playing');
                    await playAudioFile('/static/audio/Nancy.wav');
                    
                    // انتظار قصير
                    await new Promise(resolve => setTimeout(resolve, 500));
                    
                    // 4. بدء الريل تايم وتفعيل المايك
                    updateStatus('🎤 بدء تفعيل المايك...', 'realtime');
                    
                    // طلب إذن استخدام المايك
                    try {
                        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
                        updateStatus('✅ المايك مفعل - الريل تايم نشط - يمكنك الآن التحدث', 'realtime');
                        
                        // إعداد مراقبة مستوى الصوت
                        setupAudioAnalyzer(stream);
                        
                        // محاكاة اتصال WebSocket
                        connectWebSocket();
                        
                        // حفظ stream للإغلاق لاحقاً
                        window.currentMicStream = stream;
                        
                    } catch (micError) {
                        console.error('خطأ في تفعيل المايك:', micError);
                        updateStatus('❌ فشل في تفعيل المايك - تحقق من الأذونات', 'idle');
                        updateButtons(false);
                    }
                    
                } catch (error) {
                    console.error('خطأ في تشغيل التسلسل:', error);
                    updateStatus('❌ خطأ في تشغيل الصوت', 'idle');
                    updateButtons(false);
                }
            }
            
            function connectWebSocket() {
                // اتصال حقيقي بالريل تايم عبر التطبيق الأساسي
                updateStatus('🌐 محاولة الاتصال بالريل تايم...', 'realtime');
                
                try {
                    // الاتصال بـ WebSocket الحقيقي
                    const wsUrl = 'ws://localhost:8765/realtime';
                    websocket = new WebSocket(wsUrl);
                    
                    websocket.onopen = function() {
                        console.log('WebSocket متصل بنجاح');
                        updateStatus('✅ متصل بالريل تايم - يمكنك الآن التحدث', 'realtime');
                        
                        // إرسال أمر تحديث الجلسة
                        const sessionUpdate = {
                            type: "session.update",
                            session: {
                                turn_detection: {
                                    type: "server_vad"
                                }
                            }
                        };
                        websocket.send(JSON.stringify(sessionUpdate));
                    };
                    
                    websocket.onmessage = function(event) {
                        console.log('رسالة من الريل تايم:', event.data);
                        try {
                            const message = JSON.parse(event.data);
                            
                            if (message.type === 'response.audio.delta') {
                                // تشغيل الصوت المستلم من الذكاء الاصطناعي
                                playReceivedAudio(message.delta);
                            } else if (message.type === 'input_audio_buffer.speech_started') {
                                console.log('بدء الكلام مكتشف');
                            }
                        } catch (e) {
                            console.error('خطأ في تحليل رسالة الريل تايم:', e);
                        }
                    };
                    
                    websocket.onerror = function(error) {
                        console.error('خطأ في WebSocket:', error);
                        updateStatus('❌ خطأ في الاتصال بالريل تايم', 'idle');
                    };
                    
                    websocket.onclose = function() {
                        console.log('تم إغلاق اتصال الريل تايم');
                        updateStatus('🔌 تم قطع الاتصال مع الريل تايم', 'idle');
                    };
                    
                } catch (error) {
                    console.error('خطأ في إعداد WebSocket:', error);
                    updateStatus('❌ فشل في الاتصال بالريل تايم', 'idle');
                }
            }
            
            function setupAudioAnalyzer(stream) {
                // إعداد Web Audio API لمراقبة مستوى الصوت
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                analyzer = audioContext.createAnalyser();
                const microphone = audioContext.createMediaStreamSource(stream);
                
                analyzer.fftSize = 256;
                microphone.connect(analyzer);
                
                // إظهار مؤشر المايك
                document.getElementById('micIndicator').classList.add('active');
                
                // بدء مراقبة مستوى الصوت
                startVolumeMonitoring();
                
                // بدء تسجيل الصوت وإرساله للريل تايم
                startAudioCapture(stream);
            }
            
            function startVolumeMonitoring() {
                const dataArray = new Uint8Array(analyzer.frequencyBinCount);
                const volumeLevel = document.getElementById('volumeLevel');
                
                volumeCheckInterval = setInterval(() => {
                    analyzer.getByteFrequencyData(dataArray);
                    
                    // حساب متوسط مستوى الصوت
                    let sum = 0;
                    for (let i = 0; i < dataArray.length; i++) {
                        sum += dataArray[i];
                    }
                    const average = sum / dataArray.length;
                    
                    // تحويل إلى نسبة مئوية
                    const percentage = (average / 255) * 100;
                    volumeLevel.style.width = percentage + '%';
                    
                }, 100);
            }
            
            function playReceivedAudio(base64Audio) {
                // تشغيل الصوت المستلم من الذكاء الاصطناعي
                try {
                    const audioData = atob(base64Audio);
                    const arrayBuffer = new ArrayBuffer(audioData.length);
                    const view = new Uint8Array(arrayBuffer);
                    
                    for (let i = 0; i < audioData.length; i++) {
                        view[i] = audioData.charCodeAt(i);
                    }
                    
                    audioContext.decodeAudioData(arrayBuffer)
                        .then(buffer => {
                            const source = audioContext.createBufferSource();
                            source.buffer = buffer;
                            source.connect(audioContext.destination);
                            source.start();
                        })
                        .catch(error => {
                            console.error('خطأ في تشغيل الصوت:', error);
                        });
                } catch (error) {
                    console.error('خطأ في معالجة الصوت:', error);
                }
            }
            
            function startAudioCapture(stream) {
                // بدء تسجيل الصوت وإرساله للريل تايم
                try {
                    mediaRecorder = new MediaRecorder(stream, {
                        mimeType: 'audio/webm'
                    });
                    
                    mediaRecorder.ondataavailable = function(event) {
                        if (event.data.size > 0) {
                            audioChunks.push(event.data);
                            
                            // تحويل إلى base64 وإرسال للريل تايم
                            const reader = new FileReader();
                            reader.onload = function() {
                                const arrayBuffer = reader.result;
                                const base64 = btoa(String.fromCharCode(...new Uint8Array(arrayBuffer)));
                                
                                if (websocket && websocket.readyState === WebSocket.OPEN) {
                                    const message = {
                                        type: "input_audio_buffer.append",
                                        audio: base64
                                    };
                                    websocket.send(JSON.stringify(message));
                                }
                            };
                            reader.readAsArrayBuffer(event.data);
                        }
                    };
                    
                    // بدء التسجيل بفترات قصيرة
                    mediaRecorder.start(100);
                    
                } catch (error) {
                    console.error('خطأ في بدء تسجيل الصوت:', error);
                }
            }
            
            function stopSequence() {
                if (!isSequenceActive) return;
                
                // إيقاف أي صوت قيد التشغيل
                if (currentAudio) {
                    currentAudio.pause();
                    currentAudio = null;
                }
                
                // إيقاف تسجيل الصوت
                if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                    mediaRecorder.stop();
                    mediaRecorder = null;
                }
                
                // إيقاف مراقبة مستوى الصوت
                if (volumeCheckInterval) {
                    clearInterval(volumeCheckInterval);
                    volumeCheckInterval = null;
                }
                
                // إغلاق Web Audio Context
                if (audioContext) {
                    audioContext.close();
                    audioContext = null;
                    analyzer = null;
                }
                
                // إخفاء مؤشر المايك
                document.getElementById('micIndicator').classList.remove('active');
                
                // إغلاق المايك إذا كان مفعلاً
                if (window.currentMicStream) {
                    window.currentMicStream.getTracks().forEach(track => track.stop());
                    window.currentMicStream = null;
                }
                
                // إغلاق اتصال WebSocket إذا كان موجوداً
                if (websocket) {
                    websocket.close();
                    websocket = null;
                }
                
                updateStatus('⏹️ تم إيقاف التسلسل وإغلاق المايك', 'idle');
                updateButtons(false);
            }
            
            // التحكم بالكيبورد
            document.addEventListener('keydown', function(e) {
                if (e.code === 'Space') {
                    e.preventDefault();
                    if (!isSequenceActive) {
                        startSequence();
                    } else {
                        stopSequence();
                    }
                }
            });
            
            console.log('تطبيق اختبار التسلسل الصوتي جاهز!');
            console.log('اضغط على زر "اتصال" أو مفتاح المسافة لبدء الاختبار');
        </script>
    </body>
    </html>
    """
    return web.Response(text=html, content_type='text/html')

async def static_handler(request):
    """معالج الملفات الثابتة"""
    file_path = request.match_info['path']
    static_dir = os.path.join(os.path.dirname(__file__), 'static')
    file_full_path = os.path.join(static_dir, file_path)
    
    if not os.path.exists(file_full_path):
        return web.Response(status=404, text="File not found")
    
    # تحديد نوع المحتوى
    if file_path.endswith('.wav'):
        content_type = 'audio/wav'
    elif file_path.endswith('.mp3'):
        content_type = 'audio/mpeg'
    else:
        content_type = 'application/octet-stream'
    
    with open(file_full_path, 'rb') as f:
        return web.Response(body=f.read(), content_type=content_type)

def create_app():
    """إنشاء التطبيق"""
    app = web.Application()
    
    # إضافة المسارات
    app.router.add_get('/', index)
    app.router.add_get('/static/{path:.*}', static_handler)
    
    return app

if __name__ == '__main__':
    app = create_app()
    
    print("🚀 بدء تشغيل خادم اختبار التسلسل الصوتي...")
    print("📍 الرابط: http://localhost:8080")
    print("⏹️  للإيقاف: اضغط Ctrl+C")
    
    web.run_app(app, host='localhost', port=8080)
