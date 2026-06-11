import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMutation } from '@tanstack/react-query';
import { Loader2, User } from 'lucide-react';
import { PageHeader } from '@/components/common/PageHeader';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Separator } from '@/components/ui/separator';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { profileSchema, changePasswordSchema } from '@/schemas/auth.schema';
import { usersApi } from '@/api';
import { useAuthStore } from '@/store/authStore';
import { useToast } from '@/hooks/useToast';
import { getInitials } from '@/lib/utils';
import { useThemeStore } from '@/store/themeStore';
import { Switch } from '@/components/ui/switch';
import { unwrapData } from '@/lib/apiResponse'

export default function ProfilePage() {
  const { user, setUser } = useAuthStore();
  const { toast } = useToast();
  const { theme, setTheme } = useThemeStore();

  const profileForm = useForm({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      full_name: user?.full_name || '',
      email: user?.email || '',
      phone: user?.phone || '',
      department: user?.department || '',
      badge_number: user?.badge_number || '',
    },
  });

  const passwordForm = useForm({
    resolver: zodResolver(changePasswordSchema),
    defaultValues: { current_password: '', new_password: '', confirm_password: '' },
  });

  const profileMutation = useMutation({
    mutationFn: (data) => usersApi.update(user.id, data),
    onSuccess: (res) => {
      setUser(unwrapData(res));
      toast({ title: 'Profile updated' });
    },
    onError: (err) => toast({ title: 'Error', description: err.message, variant: 'destructive' }),
  });

  const passwordMutation = useMutation({
    mutationFn: (data) =>
      usersApi.changePassword(user.id, {
        current_password: data.current_password,
        new_password: data.new_password,
      }),
    onSuccess: () => {
      toast({ title: 'Password changed' });
      passwordForm.reset();
    },
    onError: (err) => toast({ title: 'Error', description: err.message, variant: 'destructive' }),
  });

  return (
    <div className="space-y-6 max-w-2xl">
      <PageHeader title="Profile & Settings" description="Manage your account and preferences" />
      <Card>
        <CardContent className="pt-6 flex items-center gap-4">
          <Avatar className="h-16 w-16">
            <AvatarFallback className="text-lg">{getInitials(user?.full_name)}</AvatarFallback>
          </Avatar>
          <div>
            <h2 className="text-xl font-semibold">{user?.full_name}</h2>
            <p className="text-muted-foreground">{user?.email}</p>
            <p className="text-sm capitalize text-primary">{user?.role}</p>
          </div>
        </CardContent>
      </Card>
      <Tabs defaultValue="profile">
        <TabsList>
          <TabsTrigger value="profile">Profile</TabsTrigger>
          <TabsTrigger value="security">Security</TabsTrigger>
          <TabsTrigger value="preferences">Preferences</TabsTrigger>
        </TabsList>
        <TabsContent value="profile">
          <Card>
            <CardHeader>
              <CardTitle className="flex items-center gap-2"><User className="h-5 w-5" />Personal Information</CardTitle>
            </CardHeader>
            <CardContent>
              <form onSubmit={profileForm.handleSubmit((d) => profileMutation.mutate(d))} className="space-y-4">
                <div className="grid gap-4 sm:grid-cols-2">
                  <div className="space-y-2 sm:col-span-2">
                    <Label>Full Name</Label>
                    <Input {...profileForm.register('full_name')} />
                  </div>
                  <div className="space-y-2">
                    <Label>Email</Label>
                    <Input type="email" {...profileForm.register('email')} />
                  </div>
                  <div className="space-y-2">
                    <Label>Phone</Label>
                    <Input {...profileForm.register('phone')} />
                  </div>
                  {user?.role === 'officer' && (
                    <>
                      <div className="space-y-2">
                        <Label>Department</Label>
                        <Input {...profileForm.register('department')} />
                      </div>
                      <div className="space-y-2">
                        <Label>Badge Number</Label>
                        <Input {...profileForm.register('badge_number')} />
                      </div>
                    </>
                  )}
                </div>
                <Button type="submit" disabled={profileMutation.isPending}>
                  {profileMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Save Changes
                </Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="security">
          <Card>
            <CardHeader><CardTitle>Change Password</CardTitle></CardHeader>
            <CardContent>
              <form onSubmit={passwordForm.handleSubmit((d) => passwordMutation.mutate(d))} className="space-y-4">
                <div className="space-y-2">
                  <Label>Current Password</Label>
                  <Input type="password" {...passwordForm.register('current_password')} />
                </div>
                <div className="space-y-2">
                  <Label>New Password</Label>
                  <Input type="password" {...passwordForm.register('new_password')} />
                </div>
                <div className="space-y-2">
                  <Label>Confirm Password</Label>
                  <Input type="password" {...passwordForm.register('confirm_password')} />
                  {passwordForm.formState.errors.confirm_password && (
                    <p className="text-sm text-destructive">{passwordForm.formState.errors.confirm_password.message}</p>
                  )}
                </div>
                <Button type="submit" disabled={passwordMutation.isPending}>Update Password</Button>
              </form>
            </CardContent>
          </Card>
        </TabsContent>
        <TabsContent value="preferences">
          <Card>
            <CardHeader><CardTitle>Appearance</CardTitle></CardHeader>
            <CardContent>
              <div className="flex items-center justify-between">
                <div>
                  <p className="font-medium">Dark Mode</p>
                  <p className="text-sm text-muted-foreground">Toggle dark/light theme</p>
                </div>
                <Switch checked={theme === 'dark'} onCheckedChange={(checked) => setTheme(checked ? 'dark' : 'light')} />
              </div>
              <Separator className="my-4" />
              <p className="text-sm text-muted-foreground">Session is managed via secure HTTP-only cookies.</p>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
}
