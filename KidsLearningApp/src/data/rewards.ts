export interface RewardItem {
    id: string;
    name: string;
    emoji: string;
    rarity: 'common' | 'rare' | 'legendary';
}

export const REWARD_DATA: RewardItem[] = [
    { id: 'plant', name: 'Plant', emoji: '🪴', rarity: 'common' },
    { id: 'bear', name: 'Teddy Bear', emoji: '🧸', rarity: 'common' },
    { id: 'ball', name: 'Ball', emoji: '⚽', rarity: 'common' },
    { id: 'robot', name: 'Robot', emoji: '🤖', rarity: 'rare' },
    { id: 'crown', name: 'Crown', emoji: '👑', rarity: 'legendary' },
    { id: 'cake', name: 'Cake', emoji: '🍰', rarity: 'common' },
    { id: 'car', name: 'Car', emoji: '🚗', rarity: 'common' },
    { id: 'rocket', name: 'Rocket', emoji: '🚀', rarity: 'rare' },
];
