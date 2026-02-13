import { HiraganaGame } from '../components/game/HiraganaGame';
import { AdditionGame } from '../components/game/AdditionGame';

interface GameProps {
    mode: 'hiragana' | 'addition';
    onBack: () => void;
}

export function Game({ mode, onBack }: GameProps) {
    return (
        <div className={`min-h-screen flex flex-col items-center justify-center p-4 relative ${mode === 'hiragana' ? 'bg-pink-50' : 'bg-green-50'}`}>
            <div className="absolute top-4 left-4 z-20">
                <button
                    onClick={onBack}
                    className="bg-white/80 hover:bg-white text-gray-800 font-bold py-2 px-6 rounded-full shadow-md backdrop-blur-sm transition-all text-lg"
                >
                    ⬅️ もどる
                </button>
            </div>

            <div className="mb-4">
                <h1 className={`text-3xl font-bold ${mode === 'hiragana' ? 'text-pink-500' : 'text-green-600'}`}>
                    {mode === 'hiragana' ? 'ひらがな クイズ' : 'たしざん ゲーム'}
                </h1>
            </div>

            {mode === 'hiragana' ? (
                <HiraganaGame />
            ) : (
                <AdditionGame />
            )}
        </div>
    );
}
