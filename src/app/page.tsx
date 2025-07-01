import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

export default function Home() {
  return (
    <main className="min-h-screen bg-background">
      {/* Debug banner to verify Tailwind is working */}
      <div className="debug-tailwind text-center">
        🎉 Tailwind CSS v4 + Orange Theme in Dark Mode is working!
      </div>

      <div className="container mx-auto px-4 py-8">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-foreground mb-4">
            SaaS App - Sales Opportunity Detection
          </h1>
          <p className="text-xl text-muted-foreground">
            AI-driven sales opportunity detection between sent emails and Pipedrive CRM
          </p>
        </div>

        {/* Shadcn/ui Components Test */}
        <div className="mb-12">
          <h2 className="text-2xl font-bold text-center mb-6 text-foreground">🧪 Orange Theme Components</h2>
          <div className="flex flex-wrap justify-center gap-4 mb-6">
            <Button variant="default">Primary Orange</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="destructive">Destructive</Button>
          </div>
          <div className="flex flex-wrap justify-center gap-2">
            <Badge variant="default">Default Badge</Badge>
            <Badge variant="secondary">Secondary Badge</Badge>
            <Badge variant="outline">Outline Badge</Badge>
            <Badge variant="destructive">Destructive Badge</Badge>
          </div>
        </div>

        {/* Test grid layout with Shadcn Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-12">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🔐 Authentication
                <Badge variant="secondary">New</Badge>
              </CardTitle>
              <CardDescription>
                Secure user authentication with Supabase
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                Learn More
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🔗 Integrations
                <Badge variant="default">Active</Badge>
              </CardTitle>
              <CardDescription>
                Connect with Pipedrive CRM and Microsoft Outlook
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                Connect
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                🤖 AI Analysis
                <Badge variant="destructive">Beta</Badge>
              </CardTitle>
              <CardDescription>
                Intelligent sales opportunity detection from emails
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                Try AI
              </Button>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                ⚡ Real-time
                <Badge variant="secondary">Live</Badge>
              </CardTitle>
              <CardDescription>
                Live dashboard updates and activity monitoring
              </CardDescription>
            </CardHeader>
            <CardContent>
              <Button className="w-full" variant="outline">
                View Dashboard
              </Button>
            </CardContent>
          </Card>
        </div>

        {/* Orange theme showcase */}
        <div className="bg-gradient-to-r from-orange-500 to-orange-600 p-8 rounded-lg text-white text-center mb-8">
          <h3 className="text-2xl font-bold mb-4">Orange Theme Showcase</h3>
          <p className="mb-6 text-orange-100">
            Beautiful orange primary colors that work perfectly in dark mode
          </p>
          <div className="flex flex-wrap justify-center gap-4">
            <Button variant="secondary" className="hover:scale-105 transition-transform">
              Hover Effect
            </Button>
            <Button variant="outline" className="bg-white/10 text-white border-white/20 hover:bg-white/20">
              Glass Effect
            </Button>
            <Badge variant="secondary" className="text-lg px-4 py-2 bg-white/20">
              Orange Badge
            </Badge>
          </div>
        </div>

        {/* Responsive test */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          <Card className="border-orange-200 dark:border-orange-800">
            <CardContent className="p-4">
              <p className="text-foreground font-semibold">Mobile: 1 column</p>
            </CardContent>
          </Card>
          <Card className="border-orange-200 dark:border-orange-800">
            <CardContent className="p-4">
              <p className="text-foreground font-semibold">Tablet: 2 columns</p>
            </CardContent>
          </Card>
          <Card className="border-orange-200 dark:border-orange-800">
            <CardContent className="p-4">
              <p className="text-foreground font-semibold">Desktop: 3+ columns</p>
            </CardContent>
          </Card>
        </div>
      </div>
    </main>
  )
} 