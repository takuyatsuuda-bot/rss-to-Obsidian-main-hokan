export interface HiraganaChar {
    char: string;
    romaji: string;
    word: string; // e.g. "Arigatou"
    emoji: string; // Placeholder for image
    options: string[]; // Options for the quiz
}

export const HIRAGANA_DATA: HiraganaChar[] = [
    { char: 'あ', romaji: 'a', word: 'あひる', emoji: '🦆', options: ['あ', 'い', 'う'] },
    { char: 'い', romaji: 'i', word: 'いちご', emoji: '🍓', options: ['い', 'あ', 'え'] },
    { char: 'う', romaji: 'u', word: 'うさぎ', emoji: '🐰', options: ['う', 'く', 'し'] },
    { char: 'え', romaji: 'e', word: 'えんぴつ', emoji: '✏️', options: ['え', 'い', 'お'] },
    { char: 'お', romaji: 'o', word: 'おにぎり', emoji: '🍙', options: ['お', 'あ', 'む'] },
];
