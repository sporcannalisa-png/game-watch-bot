import React from "react";
import { Link, useLocation } from "react-router-dom";
import { createPageUrl } from "@/utils";
import { Gamepad2, LayoutDashboard, Library, Upload, Settings, PlusCircle } from "lucide-react";
import {
  Sidebar,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarHeader,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";
import { Button } from "@/components/ui/button";

const navigationItems = [
  {
    title: "Dashboard",
    url: createPageUrl("Dashboard"),
    icon: LayoutDashboard,
  },
  {
    title: "Libreria Giochi",
    url: createPageUrl("GamesLibrary"),
    icon: Library,
  },
  {
    title: "Impostazioni",
    url: createPageUrl("Settings"),
    icon: Settings,
  }
];

export default function Layout({ children, currentPageName }) {
  const location = useLocation();

  return (
    <SidebarProvider>
      <div className="min-h-screen flex w-full bg-background">
        <Sidebar className="bg-card border-r border-border">
          <SidebarHeader className="p-4 border-b border-border">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-primary/10 rounded-lg flex items-center justify-center border border-primary/20">
                <Gamepad2 className="w-6 h-6 text-primary" />
              </div>
              <h2 className="font-bold text-xl text-foreground">GameHub</h2>
            </div>
          </SidebarHeader>
          
          <SidebarContent className="p-2 flex flex-col justify-between h-[calc(100%-150px)]">
            <SidebarGroup>
              <SidebarGroupContent>
                <SidebarMenu>
                  {navigationItems.map((item) => (
                    <SidebarMenuItem key={item.title}>
                      <SidebarMenuButton 
                        asChild 
                        className={`hover:bg-secondary transition-colors duration-200 rounded-lg mb-1 ${
                          location.pathname === item.url ? 'bg-primary/10 text-primary' : 'text-muted-foreground hover:text-foreground'
                        }`}
                      >
                        <Link to={item.url} className="flex items-center gap-3 px-3 py-2.5">
                          <item.icon className="w-5 h-5" />
                          <span className="font-medium">{item.title}</span>
                        </Link>
                      </SidebarMenuButton>
                    </SidebarMenuItem>
                  ))}
                </SidebarMenu>
              </SidebarGroupContent>
            </SidebarGroup>
          </SidebarContent>

          <div className="p-4 border-t border-border">
            <Button asChild className="w-full bg-primary text-primary-foreground hover:bg-primary/90">
                <Link to={createPageUrl("ImportGames")}>
                    <PlusCircle className="w-5 h-5 mr-2"/>
                    Aggiungi Gioco
                </Link>
            </Button>
          </div>
        </Sidebar>

        <main className="flex-1 flex flex-col">
          <header className="bg-background/80 backdrop-blur-sm border-b border-border px-6 py-4 md:hidden sticky top-0 z-10">
            <div className="flex items-center gap-4">
              <SidebarTrigger className="hover:bg-secondary p-2 rounded-lg" />
              <h1 className="text-xl font-semibold">GameHub</h1>
            </div>
          </header>

          <div className="flex-1 overflow-auto p-4 md:p-6">
            {children}
          </div>
        </main>
      </div>
    </SidebarProvider>
  );
}