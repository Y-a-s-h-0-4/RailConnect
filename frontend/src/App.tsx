import { useState } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Search, Train, ArrowRight, Clock, Banknote, Calendar, Zap, AlertCircle } from 'lucide-react'
import axios from 'axios'

const API_URL = "https://railconnect-ofqg.onrender.com/api"

type Leg = {
    train_number: string
    train_name: string
    from: string
    to: string
    departure: string
    arrival: string
}

type RouteParams = {
    type: string
    train_number?: string
    train_name?: string
    departure?: string
    arrival?: string
    duration_mins?: number
    switches: number
    leg1?: Leg
    leg2?: Leg
    layover_mins?: number
    transfer_station?: string
    transfer_station_name?: string
    leg3?: Leg
    layover_mins2?: number
    transfer_station2?: string
    transfer_station_name2?: string
    total_duration_mins?: number
}

function formatDuration(mins: number) {
    const h = Math.floor(mins / 60)
    const m = mins % 60
    return `${h}h ${m}m`
}

export default function App() {
    const [source, setSource] = useState('NDLS')
    const [destination, setDestination] = useState('BCT')
    const [date, setDate] = useState('2026-03-01')
    const [criteria, setCriteria] = useState('fastest')

    const [routes, setRoutes] = useState<RouteParams[]>([])
    const [loading, setLoading] = useState(false)
    const [error, setError] = useState('')

    const handleSearch = async (e: React.FormEvent) => {
        e.preventDefault()
        setLoading(true)
        setError('')
        try {
            const res = await axios.get(`${API_URL}/routes`, {
                params: { source, destination, date, criteria, switches: '0,1' }
            })
            setRoutes(res.data.routes)
        } catch (err) {
            setError('Failed to fetch routes. Ensure backend is running.')
            console.error(err)
        } finally {
            setLoading(false)
        }
    }

    return (
        <div className="min-h-screen bg-background relative overflow-hidden font-sans">
            {/* Dynamic Background Effects */}
            <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] bg-purple-600/20 rounded-full blur-[120px] pointer-events-none" />
            <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-pink-600/10 rounded-full blur-[150px] pointer-events-none" />

            <main className="relative z-10 max-w-5xl mx-auto px-4 py-12 md:py-20 flex flex-col items-center">

                <motion.div
                    initial={{ opacity: 0, y: -20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="text-center mb-12"
                >
                    <h1 className="text-5xl md:text-7xl font-bold tracking-tight mb-4 text-white">
                        <span className="gradient-text">Rail</span> Connect
                    </h1>
                    <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
                        Find the optimal connecting train routes leveraging advanced multi-criteria graph searches.
                    </p>
                </motion.div>

                {/* Search Panel */}
                <motion.div
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="w-full glass-panel rounded-2xl p-6 md:p-8 mb-12"
                >
                    <form onSubmit={handleSearch} className="flex flex-col md:flex-row gap-4 items-end">
                        <div className="w-full">
                            <label className="text-sm font-medium text-muted-foreground mb-2 block">Source Station</label>
                            <div className="relative">
                                <Train className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
                                <input
                                    type="text"
                                    value={source}
                                    onChange={e => setSource(e.target.value.toUpperCase())}
                                    className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all uppercase placeholder:normal-case"
                                    placeholder="e.g. NDLS"
                                    required
                                />
                            </div>
                        </div>

                        <div className="hidden md:flex items-center justify-center pb-3">
                            <ArrowRight className="text-muted-foreground" />
                        </div>

                        <div className="w-full">
                            <label className="text-sm font-medium text-muted-foreground mb-2 block">Destination Station</label>
                            <div className="relative">
                                <Train className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
                                <input
                                    type="text"
                                    value={destination}
                                    onChange={e => setDestination(e.target.value.toUpperCase())}
                                    className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all uppercase placeholder:normal-case"
                                    placeholder="e.g. BCT"
                                    required
                                />
                            </div>
                        </div>

                        <div className="w-full">
                            <label className="text-sm font-medium text-muted-foreground mb-2 block">Date</label>
                            <div className="relative">
                                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-5 h-5" />
                                <input
                                    type="date"
                                    value={date}
                                    onChange={e => setDate(e.target.value)}
                                    className="w-full bg-black/40 border border-white/10 rounded-xl py-3 pl-10 pr-4 text-white focus:outline-none focus:ring-2 focus:ring-purple-500 transition-all"
                                    required
                                    style={{ colorScheme: 'dark' }}
                                />
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full md:w-auto px-8 py-3 bg-white text-black font-semibold rounded-xl hover:bg-white/90 transition-all flex items-center justify-center gap-2 whitespace-nowrap disabled:opacity-50"
                        >
                            {loading ? <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1 }}><Zap className="w-5 h-5" /></motion.div> : <Search className="w-5 h-5" />}
                            {loading ? 'Searching...' : 'Search Routes'}
                        </button>
                    </form>

                    {/* Criteria Filters */}
                    <div className="mt-6 flex flex-wrap gap-3">
                        {[
                            { id: 'fastest', label: 'Fastest Route', icon: Zap },
                            { id: 'fewest_switches', label: 'Fewest Switches', icon: Train },
                            { id: 'cheapest', label: 'Cheapest Fare', icon: Banknote },
                        ].map(c => (
                            <button
                                key={c.id}
                                type="button"
                                onClick={() => setCriteria(c.id)}
                                className={`px-4 py-2 rounded-lg text-sm font-medium flex items-center gap-2 transition-all ${criteria === c.id
                                    ? 'bg-purple-500/20 text-purple-300 border border-purple-500/50'
                                    : 'bg-black/40 text-muted-foreground border border-white/5 hover:bg-white/5'
                                    }`}
                            >
                                <c.icon className="w-4 h-4" />
                                {c.label}
                            </button>
                        ))}
                    </div>
                </motion.div>

                {/* Results Info */}
                {error && (
                    <div className="w-full p-4 bg-red-500/10 border border-red-500/20 rounded-xl flex items-center gap-3 text-red-400 mb-8">
                        <AlertCircle className="w-5 h-5" />
                        <p>{error}</p>
                    </div>
                )}

                {/* Results List */}
                <div className="w-full space-y-6">
                    <AnimatePresence>
                        {!loading && routes.map((route, idx) => (
                            <motion.div
                                key={idx}
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                exit={{ opacity: 0, y: -20 }}
                                transition={{ delay: idx * 0.1 }}
                                className="w-full glass-panel rounded-2xl p-6 group hover:border-purple-500/30 transition-all"
                            >
                                {route.type === 'direct' ? (
                                    // Direct Train
                                    <div className="flex flex-col md:flex-row justify-between md:items-center gap-6">
                                        <div className="flex-1">
                                            <div className="flex items-center gap-3 mb-2">
                                                <span className="px-2.5 py-1 rounded-md bg-green-500/20 text-green-400 text-xs font-bold uppercase tracking-wider">
                                                    Direct
                                                </span>
                                                <span className="text-lg font-semibold text-white">{route.train_name}</span>
                                                <span className="text-muted-foreground text-sm">#{route.train_number}</span>
                                            </div>
                                            <div className="flex items-center gap-6 mt-4">
                                                <div>
                                                    <p className="text-xl font-bold text-white">{route.departure?.split(' ')[1]}</p>
                                                    <p className="text-sm font-medium text-white mb-1">{route.departure?.split(' ')[0]}</p>
                                                    <p className="text-sm text-muted-foreground">{source}</p>
                                                </div>
                                                <div className="flex-1 flex flex-col items-center px-4 relative">
                                                    <p className="text-xs text-muted-foreground mb-1">{formatDuration(route.duration_mins || 0)}</p>
                                                    <div className="w-full h-[2px] bg-white/10 relative">
                                                        <div className="absolute top-1/2 left-0 w-full h-[2px] bg-gradient-to-r from-green-500/50 to-emerald-500/50 -translate-y-1/2 origin-left scale-x-0 group-hover:scale-x-100 transition-transform duration-700" />
                                                    </div>
                                                </div>
                                                <div className="text-right">
                                                    <p className="text-xl font-bold text-white">{route.arrival?.split(' ')[1]}</p>
                                                    <p className="text-sm font-medium text-white mb-1">{route.arrival?.split(' ')[0]}</p>
                                                    <p className="text-sm text-muted-foreground">{destination}</p>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                ) : (
                                    // Connecting Train
                                    <div className="flex flex-col gap-6">
                                        <div className="flex items-center gap-3">
                                            <span className="px-2.5 py-1 rounded-md bg-purple-500/20 text-purple-400 text-xs font-bold uppercase tracking-wider">
                                                {route.switches === 1 ? '1 Switch' : '2 Switches'}
                                            </span>
                                            <span className="text-muted-foreground text-sm flex items-center gap-2">
                                                <Clock className="w-4 h-4" />
                                                Total: {formatDuration(route.total_duration_mins || 0)}
                                            </span>
                                        </div>

                                        <div className="relative pl-8 before:absolute before:inset-y-2 before:left-[11px] before:w-[2px] before:bg-white/10 space-y-8">
                                            {/* Leg 1 */}
                                            <div className="relative">
                                                <div className="absolute -left-[37px] top-1.5 w-4 h-4 rounded-full bg-background border-[3px] border-purple-500 z-10" />
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <p className="text-xl font-bold text-white">{route.leg1?.departure.split(' ')[1]}</p>
                                                        <p className="text-xs font-medium text-white mb-1">{route.leg1?.departure.split(' ')[0]}</p>
                                                        <p className="text-sm font-medium text-muted-foreground">{route.leg1?.from}</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-medium text-white">{route.leg1?.train_name}</p>
                                                        <p className="text-sm text-muted-foreground">#{route.leg1?.train_number}</p>
                                                    </div>
                                                </div>
                                                <div className="my-3 flex justify-between items-center bg-white/5 rounded-lg p-3 border border-white/5">
                                                    <p className="text-sm text-muted-foreground">Arrives at {route.leg1?.arrival}</p>
                                                    <ArrowRight className="w-4 h-4 text-muted-foreground" />
                                                </div>
                                            </div>

                                            {/* Layover */}
                                            <div className="relative py-2 pl-4 border-l-2 border-dashed border-orange-500/30 -ml-4">
                                                <div className="absolute top-1/2 -left-[5px] w-2 h-2 rounded-full bg-orange-500 -translate-y-1/2" />
                                                <p className="text-sm text-orange-400 font-medium">
                                                    {formatDuration(route.layover_mins || 0)} layover at {route.transfer_station_name} ({route.transfer_station})
                                                </p>
                                            </div>

                                            {/* Leg 2 */}
                                            <div className="relative">
                                                <div className={`absolute -left-[37px] top-1.5 w-4 h-4 rounded-full bg-background border-[3px] ${route.switches === 1 ? 'border-emerald-500' : 'border-blue-500'} z-10`} />
                                                <div className="flex justify-between items-start">
                                                    <div>
                                                        <p className="text-xl font-bold text-white">{route.leg2?.departure.split(' ')[1]}</p>
                                                        <p className="text-xs font-medium text-white mb-1">{route.leg2?.departure.split(' ')[0]}</p>
                                                        <p className="text-sm font-medium text-muted-foreground">{route.leg2?.from}</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="font-medium text-white">{route.leg2?.train_name}</p>
                                                        <p className="text-sm text-muted-foreground">#{route.leg2?.train_number}</p>
                                                    </div>
                                                </div>

                                                {route.switches === 2 && (
                                                    <div className="my-3 flex justify-between items-center bg-white/5 rounded-lg p-3 border border-white/5">
                                                        <p className="text-sm text-muted-foreground">Arrives at {route.leg2?.arrival}</p>
                                                        <ArrowRight className="w-4 h-4 text-muted-foreground" />
                                                    </div>
                                                )}

                                                {route.switches === 1 && (
                                                    <div className="mt-4 flex justify-between items-center">
                                                        <div>
                                                            <p className="text-xl font-bold text-white">{route.leg2?.arrival.split(' ')[1]}</p>
                                                            <p className="text-xs font-medium text-white mb-1">{route.leg2?.arrival.split(' ')[0]}</p>
                                                            <p className="text-sm font-medium text-muted-foreground">{route.leg2?.to}</p>
                                                        </div>
                                                    </div>
                                                )}
                                            </div>

                                            {route.switches === 2 && (
                                                <>
                                                    {/* Layover 2 */}
                                                    <div className="relative py-2 pl-4 border-l-2 border-dashed border-orange-500/30 -ml-4">
                                                        <div className="absolute top-1/2 -left-[5px] w-2 h-2 rounded-full bg-orange-500 -translate-y-1/2" />
                                                        <p className="text-sm text-orange-400 font-medium">
                                                            {formatDuration(route.layover_mins2 || 0)} layover at {route.transfer_station_name2} ({route.transfer_station2})
                                                        </p>
                                                    </div>

                                                    {/* Leg 3 */}
                                                    <div className="relative">
                                                        <div className="absolute -left-[37px] top-1.5 w-4 h-4 rounded-full bg-background border-[3px] border-emerald-500 z-10" />
                                                        <div className="flex justify-between items-start">
                                                            <div>
                                                                <p className="text-xl font-bold text-white">{route.leg3?.departure.split(' ')[1]}</p>
                                                                <p className="text-xs font-medium text-white mb-1">{route.leg3?.departure.split(' ')[0]}</p>
                                                                <p className="text-sm font-medium text-muted-foreground">{route.leg3?.from}</p>
                                                            </div>
                                                            <div className="text-right">
                                                                <p className="font-medium text-white">{route.leg3?.train_name}</p>
                                                                <p className="text-sm text-muted-foreground">#{route.leg3?.train_number}</p>
                                                            </div>
                                                        </div>
                                                        <div className="mt-4 flex justify-between items-center">
                                                            <div>
                                                                <p className="text-xl font-bold text-white">{route.leg3?.arrival.split(' ')[1]}</p>
                                                                <p className="text-xs font-medium text-white mb-1">{route.leg3?.arrival.split(' ')[0]}</p>
                                                                <p className="text-sm font-medium text-muted-foreground">{route.leg3?.to}</p>
                                                            </div>
                                                        </div>
                                                    </div>
                                                </>
                                            )}
                                        </div>

                                    </div>
                                )}
                            </motion.div>
                        ))}
                    </AnimatePresence>

                    {!loading && routes.length === 0 && !error && (
                        <div className="text-center py-12 text-muted-foreground">
                            <Train className="w-12 h-12 mx-auto mb-4 opacity-20" />
                            <p>Enter your source and destination to find optimal connections.</p>
                        </div>
                    )}
                </div>
            </main >
        </div >
    )
}
