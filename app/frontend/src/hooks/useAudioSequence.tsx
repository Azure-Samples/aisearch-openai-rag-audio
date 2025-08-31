import { useCallback } from 'react';

interface UseAudioSequenceProps {
    onSequenceComplete: () => void;
}

const useAudioSequence = ({ onSequenceComplete }: UseAudioSequenceProps) => {
    const playAudioSequence = useCallback(async () => {
        try {
            console.log('Starting audio sequence...');
            
            // 1. تشغيل Ran.mp3 (الرنة)
            console.log('Playing Ran.mp3...');
            const ranAudio = new Audio('/audio/Ran.mp3');
            
            await new Promise<void>((resolve, reject) => {
                ranAudio.onended = () => {
                    console.log('Ran.mp3 ended');
                    resolve();
                };
                ranAudio.onerror = (error) => {
                    console.error('Error playing Ran.mp3:', error);
                    reject(error);
                };
                ranAudio.play().catch(reject);
            });

            // 2. انتظار قصير قبل تشغيل between.wav
            console.log('Waiting before between.wav...');
            await new Promise(resolve => setTimeout(resolve, 500));

            // 3. تشغيل between.wav
            console.log('Playing between.wav...');
            const betweenAudio = new Audio('/audio/between.wav');
            
            await new Promise<void>((resolve, reject) => {
                betweenAudio.onended = () => {
                    console.log('between.wav ended');
                    resolve();
                };
                betweenAudio.onerror = (error) => {
                    console.error('Error playing between.wav:', error);
                    reject(error);
                };
                betweenAudio.play().catch(reject);
            });

            // 4. انتظار قصير قبل تشغيل Nancy.wav
            console.log('Waiting before Nancy.wav...');
            await new Promise(resolve => setTimeout(resolve, 500));

            // 5. تشغيل Nancy.wav
            console.log('Playing Nancy.wav...');
            const nancyAudio = new Audio('/audio/Nancy.wav');
            
            await new Promise<void>((resolve, reject) => {
                nancyAudio.onended = () => {
                    console.log('Nancy.wav ended');
                    resolve();
                };
                nancyAudio.onerror = (error) => {
                    console.error('Error playing Nancy.wav:', error);
                    reject(error);
                };
                nancyAudio.play().catch(reject);
            });

            // 6. انتظار قصير قبل تمكين الـ Realtime
            console.log('Waiting before enabling Realtime...');
            await new Promise(resolve => setTimeout(resolve, 500));

            // 7. استدعاء الدالة للإشارة إلى انتهاء التسلسل
            console.log('Audio sequence completed, calling onSequenceComplete');
            onSequenceComplete();

        } catch (error) {
            console.error('Error playing audio sequence:', error);
            // في حالة حدوث خطأ، مازلنا نريد تمكين الـ Realtime
            console.error('Audio sequence failed, calling onSequenceComplete anyway');
            onSequenceComplete();
        }
    }, [onSequenceComplete]);

    return {
        playAudioSequence
    };
};

export default useAudioSequence;
