import { useState } from 'react';
import { Home } from './screens/Home';
import { Game } from './screens/Game';
import { Room } from './screens/Room';

type Screen = 'home' | 'hiragana' | 'addition' | 'room';

function App() {
  const [currentScreen, setCurrentScreen] = useState<Screen>('home');

  return (
    <>
      {currentScreen === 'home' && (
        <Home
          onStartHiragana={() => setCurrentScreen('hiragana')}
          onStartAddition={() => setCurrentScreen('addition')}
          onOpenRoom={() => setCurrentScreen('room')}
        />
      )}
      {(currentScreen === 'hiragana' || currentScreen === 'addition') && (
        <Game
          mode={currentScreen}
          onBack={() => setCurrentScreen('home')}
        />
      )}
      {currentScreen === 'room' && (
        <Room onBack={() => setCurrentScreen('home')} />
      )}
    </>
  );
}

export default App;
