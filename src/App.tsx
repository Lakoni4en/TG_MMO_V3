
import { useState } from 'react'

const CLASSES = [
  { id: 'warrior', icon: '⚔️', name: 'Warrior', desc: 'Strong melee fighter with high HP', color: 'from-red-500 to-orange-600' },
  { id: 'mage', icon: '🔮', name: 'Mage', desc: 'Master of spells with devastating power', color: 'from-violet-500 to-purple-700' },
  { id: 'rogue', icon: '🗡️', name: 'Rogue', desc: 'Fast assassin with critical strikes', color: 'from-gray-600 to-gray-900' },
  { id: 'paladin', icon: '🛡️', name: 'Paladin', desc: 'Holy warrior who heals & protects', color: 'from-yellow-400 to-amber-600' },
  { id: 'ranger', icon: '🏹', name: 'Ranger', desc: 'Swift archer with poison arrows', color: 'from-green-500 to-emerald-700' },
  { id: 'necromancer', icon: '💀', name: 'Necromancer', desc: 'Dark mage controlling undead', color: 'from-teal-600 to-cyan-900' },
]

const RACES = [
  { icon: '👤', name: 'Human', bonus: '+10% all stats, bonus skill point' },
  { icon: '🧝', name: 'Elf', bonus: '+25% speed & mana, dodge bonus' },
  { icon: '⛏️', name: 'Dwarf', bonus: '+30% HP & defense, crafting bonus' },
  { icon: '👹', name: 'Orc', bonus: '+40% attack, double rage damage' },
  { icon: '💀', name: 'Undead', bonus: 'Immune to poison, +20% dark magic' },
  { icon: '😈', name: 'Demon', bonus: '+30% fire damage, life steal' },
]

const MAPS = [
  { icon: '🌲', name: 'Whispering Forest', level: 1, desc: 'Dense forest with wolves & goblins', color: 'bg-green-900' },
  { icon: '🌾', name: 'Golden Plains', level: 5, desc: 'Open fields with bandits & boars', color: 'bg-yellow-900' },
  { icon: '🕳️', name: 'Dark Caverns', level: 10, desc: 'Underground with golems & spiders', color: 'bg-stone-900' },
  { icon: '⚰️', name: 'Ancient Dungeon', level: 20, desc: 'Ruins full of undead horrors', color: 'bg-gray-900' },
  { icon: '🌊', name: 'Cursed Swamp', level: 25, desc: 'Toxic marshlands with shadows', color: 'bg-teal-900' },
  { icon: '🌋', name: 'Inferno Volcano', level: 40, desc: 'Scorching fire demons & dragons', color: 'bg-red-900' },
  { icon: '❄️', name: 'Frozen Tundra', level: 60, desc: 'Icy wasteland with frost titans', color: 'bg-blue-900' },
  { icon: '🌌', name: 'Void Realm', level: 80, desc: 'Dimension beyond reality. MAX danger!', color: 'bg-indigo-950' },
]

const FEATURES = [
  { icon: '⚔️', title: '6 Unique Classes', desc: 'Warrior, Mage, Rogue, Paladin, Ranger, Necromancer' },
  { icon: '🌍', title: '6 Playable Races', desc: 'Human, Elf, Dwarf, Orc, Undead, Demon — each with unique bonuses' },
  { icon: '🗺️', title: '8 Explorable Maps', desc: 'From beginner forests to the terrifying Void Realm' },
  { icon: '📚', title: '100+ Skills', desc: 'Deep skill tree with hidden & secret unlockable skills' },
  { icon: '🤖', title: 'Auto-Battle', desc: 'Purchase the chip and fight automatically while you rest' },
  { icon: '💀', title: 'Hardcore Mode', desc: '1 life, 2.5x EXP — reach LVL 100 to earn the Immortal title!' },
  { icon: '⚒️', title: 'Crafting System', desc: 'Gather materials and craft powerful items & potions' },
  { icon: '🔍', title: 'Exploration', desc: 'Search maps for rare hidden items and secret discoveries' },
  { icon: '🏆', title: 'Achievements', desc: '15+ achievements including secret ones tied to kill milestones' },
  { icon: '🎯', title: 'Secret Skills', desc: 'Kill 1000 Slimes, 100 Dragons, or die 50 times to unlock secrets' },
  { icon: '🧪', title: 'Promo Codes', desc: 'Use special codes for temporary boosts!' },
  { icon: '👑', title: 'Boss Battles', desc: '8 epic map bosses with massive rewards' },
]

const COMMANDS = [
  { cmd: '/start', desc: 'Start the game or view main menu' },
  { cmd: '/stats', desc: 'View your character statistics' },
  { cmd: '/battle', desc: 'Fight monsters on your current map' },
  { cmd: '/map', desc: 'View world map and travel' },
  { cmd: '/skills', desc: 'Open skill tree & learn skills' },
  { cmd: '/shop', desc: 'Buy items, potions, equipment' },
  { cmd: '/inventory', desc: 'View and use your items' },
  { cmd: '/explore', desc: 'Search the map for hidden items' },
  { cmd: '/craft', desc: 'Craft items from materials' },
  { cmd: '/auto', desc: 'Toggle auto-battle mode' },
  { cmd: '/promo', desc: 'Enter a promo code (try Premak4!)' },
  { cmd: '/achievements', desc: 'View your achievement list' },
  { cmd: '/help', desc: 'Show all commands and tips' },
  { cmd: '/reset', desc: '⚠️ Delete character and restart' },
]

const SECRET_SKILLS = [
  { icon: '🟢', name: 'Slime Mastery', condition: 'Kill 1,000 Slimes' },
  { icon: '🐺', name: 'Wolf Bond', condition: 'Kill 1,000 Wolves' },
  { icon: '🐉', name: 'Dragon Slayer', condition: 'Kill 100 Dragons' },
  { icon: '💀', name: 'Undying Will', condition: 'Die 50 times' },
  { icon: '🌑', name: 'Shadow Dancer', condition: 'Kill 500 Shadows' },
  { icon: '🌌', name: 'Void Walker', condition: 'Kill 200 Demons' },
  { icon: '📜', name: 'Ancient Knowledge', condition: 'Explore all 8 maps' },
  { icon: '✨', name: 'Immortal Soul', condition: 'Reach LVL 100 Hardcore' },
  { icon: '👑', name: 'Coin Emperor', condition: 'Earn 1,000,000 coins total' },
  { icon: '🪨', name: 'Golem Breaker', condition: 'Kill 300 Stone Golems' },
]

function Tab({ active, onClick, children }: { active: boolean; onClick: () => void; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className={`px-4 py-2 rounded-lg text-sm font-semibold transition-all duration-200 ${
        active
          ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/30'
          : 'text-gray-400 hover:text-white hover:bg-white/5'
      }`}
    >
      {children}
    </button>
  )
}

function Card({ children, className = '' }: { children: React.ReactNode; className?: string }) {
  return (
    <div className={`bg-white/5 border border-white/10 rounded-xl p-5 backdrop-blur-sm hover:bg-white/8 transition-all ${className}`}>
      {children}
    </div>
  )
}

export default function App() {
  const [activeTab, setActiveTab] = useState<'overview' | 'classes' | 'maps' | 'skills' | 'commands' | 'setup'>('overview')
  const [copied, setCopied] = useState(false)

  const copyPromo = () => {
    navigator.clipboard.writeText('Premak4')
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] text-white font-sans">
      {/* Animated background */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none">
        <div className="absolute -top-40 -left-40 w-80 h-80 bg-violet-600/20 rounded-full blur-3xl animate-pulse" />
        <div className="absolute top-1/2 -right-40 w-96 h-96 bg-blue-600/15 rounded-full blur-3xl animate-pulse delay-1000" />
        <div className="absolute -bottom-40 left-1/3 w-80 h-80 bg-purple-600/15 rounded-full blur-3xl animate-pulse delay-2000" />
      </div>

      {/* Header */}
      <header className="relative border-b border-white/10 bg-black/30 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-gradient-to-br from-violet-500 to-purple-700 rounded-xl flex items-center justify-center text-xl shadow-lg shadow-violet-500/30">
              ⚔️
            </div>
            <div>
              <h1 className="text-xl font-black bg-gradient-to-r from-violet-400 to-purple-300 bg-clip-text text-transparent">
                ABYSS CHRONICLES
              </h1>
              <p className="text-xs text-gray-500">Telegram MMORPG Bot</p>
            </div>
          </div>
          <div className="flex items-center gap-2">
            <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            <span className="text-green-400 text-sm font-medium">Online</span>
          </div>
        </div>
      </header>

      <main className="relative max-w-6xl mx-auto px-4 py-8">
        {/* Hero section */}
        <div className="text-center mb-12">
          <div className="text-7xl mb-4 animate-bounce">⚔️</div>
          <h2 className="text-5xl font-black mb-4">
            <span className="bg-gradient-to-r from-violet-400 via-purple-300 to-pink-400 bg-clip-text text-transparent">
              ABYSS CHRONICLES
            </span>
          </h2>
          <p className="text-xl text-gray-400 max-w-2xl mx-auto leading-relaxed">
            A fully-featured MMORPG Telegram bot with classes, races, skills, maps, crafting,
            auto-battle, hardcore mode, and 100+ unlockable skills.
          </p>
          <div className="mt-6 flex flex-wrap justify-center gap-3">
            <span className="px-4 py-2 bg-violet-500/20 border border-violet-500/40 rounded-full text-violet-300 text-sm font-medium">
              ⚔️ 6 Classes
            </span>
            <span className="px-4 py-2 bg-blue-500/20 border border-blue-500/40 rounded-full text-blue-300 text-sm font-medium">
              🌍 6 Races
            </span>
            <span className="px-4 py-2 bg-green-500/20 border border-green-500/40 rounded-full text-green-300 text-sm font-medium">
              🗺️ 8 Maps
            </span>
            <span className="px-4 py-2 bg-yellow-500/20 border border-yellow-500/40 rounded-full text-yellow-300 text-sm font-medium">
              📚 100+ Skills
            </span>
            <span className="px-4 py-2 bg-red-500/20 border border-red-500/40 rounded-full text-red-300 text-sm font-medium">
              💀 Hardcore Mode
            </span>
          </div>
        </div>

        {/* Promo Code Banner */}
        <div className="mb-10 relative overflow-hidden rounded-2xl bg-gradient-to-r from-yellow-500/20 via-orange-500/20 to-red-500/20 border border-yellow-500/30 p-6">
          <div className="absolute inset-0 bg-gradient-to-r from-yellow-500/5 to-transparent" />
          <div className="relative flex flex-col sm:flex-row items-center justify-between gap-4">
            <div className="flex items-center gap-3">
              <span className="text-4xl">🎁</span>
              <div>
                <h3 className="text-xl font-bold text-yellow-300">Promo Code Active!</h3>
                <p className="text-gray-300 text-sm">Get 2x EXP for 24 hours with this special code:</p>
              </div>
            </div>
            <div className="flex items-center gap-3">
              <code className="px-6 py-3 bg-black/40 border border-yellow-500/50 rounded-xl text-yellow-300 font-mono text-2xl font-black tracking-widest">
                Premak4
              </code>
              <button
                onClick={copyPromo}
                className="px-4 py-3 bg-yellow-500 hover:bg-yellow-400 text-black font-bold rounded-xl transition-all active:scale-95"
              >
                {copied ? '✅' : '📋'}
              </button>
            </div>
          </div>
          <p className="relative text-center text-xs text-gray-400 mt-3">Use in-game: <code className="text-yellow-400">/promo Premak4</code></p>
        </div>

        {/* Tabs */}
        <div className="flex flex-wrap gap-2 mb-8 p-1 bg-white/5 rounded-xl border border-white/10">
          {(['overview', 'classes', 'maps', 'skills', 'commands', 'setup'] as const).map(tab => (
            <Tab key={tab} active={activeTab === tab} onClick={() => setActiveTab(tab)}>
              {tab === 'overview' && '🏠 Overview'}
              {tab === 'classes' && '⚔️ Classes & Races'}
              {tab === 'maps' && '🗺️ Maps'}
              {tab === 'skills' && '📚 Skills'}
              {tab === 'commands' && '💬 Commands'}
              {tab === 'setup' && '🚀 Setup'}
            </Tab>
          ))}
        </div>

        {/* Overview Tab */}
        {activeTab === 'overview' && (
          <div className="space-y-8">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {FEATURES.map((f, i) => (
                <Card key={i}>
                  <div className="text-3xl mb-3">{f.icon}</div>
                  <h3 className="font-bold text-white mb-1">{f.title}</h3>
                  <p className="text-sm text-gray-400">{f.desc}</p>
                </Card>
              ))}
            </div>

            {/* Game Modes */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card className="border-green-500/20">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-4xl">♾️</span>
                  <div>
                    <h3 className="text-xl font-bold text-green-400">Endless Lives Mode</h3>
                    <p className="text-xs text-gray-400">Perfect for casual play</p>
                  </div>
                </div>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>✅ Respawn on death with 30% HP</li>
                  <li>✅ Normal EXP & drop rates</li>
                  <li>✅ Full access to all content</li>
                  <li>✅ No permanent consequences</li>
                </ul>
              </Card>
              <Card className="border-red-500/20">
                <div className="flex items-center gap-3 mb-4">
                  <span className="text-4xl">💀</span>
                  <div>
                    <h3 className="text-xl font-bold text-red-400">Hardcore Mode</h3>
                    <p className="text-xs text-gray-400">For the brave only</p>
                  </div>
                </div>
                <ul className="space-y-2 text-sm text-gray-300">
                  <li>🔥 Only 1 life — death = game over</li>
                  <li>🔥 +150% EXP multiplier</li>
                  <li>🔥 x2 item drop rate</li>
                  <li>👑 Reach LVL 100 → <span className="text-yellow-400 font-bold">Immortal Title</span></li>
                  <li>✨ Can switch to Endless after LVL 100</li>
                </ul>
              </Card>
            </div>

            {/* Stat panel */}
            <Card>
              <h3 className="text-lg font-bold mb-4 text-violet-300">📊 Game Stats Preview</h3>
              <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 text-center">
                {[
                  { label: 'Classes', value: '6', icon: '⚔️' },
                  { label: 'Races', value: '6', icon: '🌍' },
                  { label: 'Maps', value: '8', icon: '🗺️' },
                  { label: 'Mobs', value: '40+', icon: '👾' },
                  { label: 'Skills', value: '100+', icon: '📚' },
                  { label: 'Secret Skills', value: '10', icon: '🔓' },
                  { label: 'Achievements', value: '15+', icon: '🏆' },
                  { label: 'Max Level', value: '100', icon: '👑' },
                ].map((stat, i) => (
                  <div key={i} className="bg-white/5 rounded-xl p-3">
                    <div className="text-2xl mb-1">{stat.icon}</div>
                    <div className="text-2xl font-black text-violet-300">{stat.value}</div>
                    <div className="text-xs text-gray-400">{stat.label}</div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        )}

        {/* Classes & Races Tab */}
        {activeTab === 'classes' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold mb-5 text-white">⚔️ Classes</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {CLASSES.map(cls => (
                  <div
                    key={cls.id}
                    className={`relative overflow-hidden rounded-xl p-5 bg-gradient-to-br ${cls.color} bg-opacity-20 border border-white/10 hover:scale-105 transition-transform cursor-pointer`}
                  >
                    <div className="text-4xl mb-3">{cls.icon}</div>
                    <h3 className="text-xl font-bold text-white">{cls.name}</h3>
                    <p className="text-sm text-white/70 mt-1">{cls.desc}</p>
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h2 className="text-2xl font-bold mb-5 text-white">🌍 Races</h2>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                {RACES.map((race, i) => (
                  <Card key={i}>
                    <div className="flex items-center gap-3 mb-2">
                      <span className="text-3xl">{race.icon}</span>
                      <h3 className="text-lg font-bold text-white">{race.name}</h3>
                    </div>
                    <p className="text-sm text-violet-300 font-medium">{race.bonus}</p>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Maps Tab */}
        {activeTab === 'maps' && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-5 text-white">🗺️ World Maps</h2>
            <div className="relative">
              {/* Map path connector */}
              <div className="absolute left-8 top-0 bottom-0 w-0.5 bg-gradient-to-b from-green-500 via-yellow-500 via-orange-500 to-indigo-500 opacity-30" />
              <div className="space-y-4">
                {MAPS.map((map, i) => (
                  <div key={i} className="relative flex items-center gap-4 ml-4">
                    <div className={`relative z-10 w-8 h-8 ${map.color} rounded-full flex items-center justify-center text-sm border-2 border-white/20 flex-shrink-0`}>
                      {map.icon}
                    </div>
                    <Card className="flex-1">
                      <div className="flex items-center justify-between flex-wrap gap-2">
                        <div>
                          <h3 className="font-bold text-white">{map.name}</h3>
                          <p className="text-sm text-gray-400">{map.desc}</p>
                        </div>
                        <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                          map.level === 1 ? 'bg-green-500/20 text-green-300' :
                          map.level <= 25 ? 'bg-yellow-500/20 text-yellow-300' :
                          map.level <= 60 ? 'bg-orange-500/20 text-orange-300' :
                          'bg-red-500/20 text-red-300'
                        }`}>
                          LVL {map.level}+
                        </span>
                      </div>
                    </Card>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Skills Tab */}
        {activeTab === 'skills' && (
          <div className="space-y-8">
            <div>
              <h2 className="text-2xl font-bold mb-2 text-white">📚 Skill System</h2>
              <p className="text-gray-400 mb-5">Each class has a skill tree with active and passive skills. Universal skills are available to all classes. Some skills are hidden and can be purchased with Skill Scrolls.</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 mb-6">
                {[
                  { type: '⚔️ Active Skills', desc: 'Use in battle, cost mana. Powerful direct effects.' },
                  { type: '🛡️ Passive Skills', desc: 'Always active. Boost stats permanently.' },
                  { type: '🌐 Universal Skills', desc: 'Available to ALL classes. General improvements.' },
                  { type: '🔒 Hidden Skills', desc: 'Not visible. Unlock via Skill Scrolls from shop.' },
                  { type: '🔓 Secret Skills', desc: 'Unlocked by gameplay achievements (kill counts, etc.).' },
                  { type: '👑 Ultimate Skills', desc: 'Powerful skills requiring LVL 40+ to unlock.' },
                ].map((t, i) => (
                  <Card key={i}>
                    <div className="font-bold text-violet-300 mb-1">{t.type}</div>
                    <p className="text-sm text-gray-400">{t.desc}</p>
                  </Card>
                ))}
              </div>
            </div>

            <div>
              <h2 className="text-2xl font-bold mb-2 text-white">🔓 Secret Skills</h2>
              <p className="text-gray-400 mb-5">These 10 secret skills unlock through specific gameplay milestones. No hints are given in-game!</p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                {SECRET_SKILLS.map((sk, i) => (
                  <Card key={i} className="border-yellow-500/20">
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{sk.icon}</span>
                      <div>
                        <div className="font-bold text-yellow-300">{sk.name}</div>
                        <div className="text-xs text-gray-400">Unlock: {sk.condition}</div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* Commands Tab */}
        {activeTab === 'commands' && (
          <div className="space-y-4">
            <h2 className="text-2xl font-bold mb-5 text-white">💬 Bot Commands</h2>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {COMMANDS.map((cmd, i) => (
                <Card key={i} className="flex items-center gap-4">
                  <code className="px-3 py-1.5 bg-violet-500/20 border border-violet-500/30 rounded-lg text-violet-300 font-mono text-sm font-bold flex-shrink-0">
                    {cmd.cmd}
                  </code>
                  <p className="text-sm text-gray-300">{cmd.desc}</p>
                </Card>
              ))}
            </div>

            {/* Auto battle info */}
            <Card className="border-blue-500/20 mt-6">
              <div className="flex items-center gap-3 mb-3">
                <span className="text-3xl">🤖</span>
                <h3 className="text-xl font-bold text-blue-300">Auto-Battle System</h3>
              </div>
              <ul className="space-y-2 text-sm text-gray-300">
                <li>• Purchase the <span className="text-yellow-300 font-bold">Auto-Battle Chip</span> from the shop for <span className="text-yellow-300">500 coins</span></li>
                <li>• Toggle on/off with <code className="text-violet-300">/auto</code> or via main menu button</li>
                <li>• Fights a random mob on your current map every <span className="text-green-300">30 seconds</span></li>
                <li>• Automatically pauses if HP drops below <span className="text-red-300">15%</span></li>
                <li>• Sends battle results directly to you!</li>
              </ul>
            </Card>
          </div>
        )}

        {/* Setup Tab */}
        {activeTab === 'setup' && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold mb-5 text-white">🚀 Deployment Guide</h2>

            <div className="space-y-4">
              {[
                {
                  step: 1, title: 'Get a Bot Token',
                  content: 'Message @BotFather on Telegram, create a bot with /newbot, and copy your token.'
                },
                {
                  step: 2, title: 'Upload to GitHub',
                  content: 'Push all files to your GitHub repository. The bot/ folder contains all game files.'
                },
                {
                  step: 3, title: 'Deploy on Railway',
                  content: 'Go to railway.app, create a new project from your GitHub repo. Set BOT_TOKEN environment variable.'
                },
                {
                  step: 4, title: 'Set Environment Variables',
                  content: 'In Railway settings, add: BOT_TOKEN = your_telegram_bot_token'
                },
                {
                  step: 5, title: 'Install Dependencies',
                  content: 'Railway auto-installs from requirements.txt. Packages: python-telegram-bot[job-queue], python-dotenv, aiosqlite'
                },
                {
                  step: 6, title: 'Launch!',
                  content: 'Railway will run "python bot/main.py" automatically. Your bot goes live!'
                },
              ].map((item) => (
                <Card key={item.step} className="flex gap-4">
                  <div className="w-10 h-10 bg-violet-500/20 border border-violet-500/40 rounded-xl flex items-center justify-center text-violet-300 font-black text-lg flex-shrink-0">
                    {item.step}
                  </div>
                  <div>
                    <h3 className="font-bold text-white mb-1">{item.title}</h3>
                    <p className="text-sm text-gray-400">{item.content}</p>
                  </div>
                </Card>
              ))}
            </div>

            <Card className="border-green-500/20">
              <h3 className="text-lg font-bold text-green-400 mb-3">📁 File Structure</h3>
              <pre className="text-sm text-gray-300 font-mono overflow-x-auto">
{`bot/
├── main.py         ← Entry point (run this)
├── config.py       ← Settings, classes, races
├── database.py     ← SQLite database functions  
├── handlers.py     ← Telegram command handlers
├── battle.py       ← Combat system
├── skills.py       ← 100+ skill definitions
├── maps.py         ← Maps, mobs, items
└── achievements.py ← Achievement definitions

requirements.txt    ← Python dependencies
Procfile           ← Railway process config
railway.json       ← Railway deployment config`}
              </pre>
            </Card>

            <Card className="border-yellow-500/20">
              <h3 className="text-lg font-bold text-yellow-400 mb-3">⚙️ Environment Variables</h3>
              <div className="space-y-2">
                <div className="flex items-center gap-3 p-3 bg-black/30 rounded-lg font-mono text-sm">
                  <span className="text-yellow-300">BOT_TOKEN</span>
                  <span className="text-gray-500">=</span>
                  <span className="text-green-300">your_bot_token_from_botfather</span>
                </div>
              </div>
              <p className="text-xs text-gray-500 mt-3">The database (SQLite) is created automatically in the working directory.</p>
            </Card>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="relative border-t border-white/10 mt-16 py-8 text-center text-gray-600 text-sm">
        <p className="text-2xl mb-2">⚔️</p>
        <p className="font-bold text-gray-400">ABYSS CHRONICLES</p>
        <p className="text-xs mt-1">Telegram MMORPG Bot — Ready for Railway Deployment</p>
      </footer>
    </div>
  )
}
