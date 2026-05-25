export function Progress({ value, className = "", ...props }: any) { 
  return (
    <div className={`relative h-4 w-full overflow-hidden rounded-full bg-slate-200 ${className}`} {...props}>
      <div className="h-full bg-blue-600 transition-all" style={{ width: `${value || 0}%` }} />
    </div>
  ) 
}
