from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario

# ===================================================================
# == FORMULÁRIOS PARA CLIENTES DO SITE (Registro e Login Externo) ==
# ===================================================================

class ClienteRegistroForm(UserCreationForm):
    """
    Formulário para novos clientes se registrarem no site.
    Usa UserCreationForm para lidar com a criação de usuário e senha de forma segura.
    """
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Seu melhor e-mail'})
    )

    class Meta(UserCreationForm.Meta):
        fields = UserCreationForm.Meta.fields + ('email',)
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário'}),
        }

class ClienteLoginForm(forms.Form):
    """
    Formulário para clientes existentes fazerem login no site.
    """
    username = forms.CharField(widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome de usuário'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'}))


# ===================================================================
# == FORMULÁRIOS PARA O PAINEL DE ADMINISTRAÇÃO (Interno) ==
# ===================================================================

class UsuarioForm(forms.ModelForm):
    """
    Formulário para o admin editar os dados de perfil de um usuário.
    Não lida com senhas.
    """
    class Meta:
        model = Usuario
        fields = ['nome', 'email', 'cpf', 'idade', 'cidade', 'pais']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'cpf': forms.TextInput(attrs={'class': 'form-control'}),
            'idade': forms.NumberInput(attrs={'class': 'form-control'}),
            'cidade': forms.TextInput(attrs={'class': 'form-control'}),
            'pais': forms.TextInput(attrs={'class': 'form-control'}),
        }

class AdminRegistrationForm(forms.Form):
    """
    Formulário para um superusuário registrar um novo administrador no painel.
    """
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    nome_completo = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nome Completo'})
    )
    password1 = forms.CharField(
        label='Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'})
    )
    password2 = forms.CharField(
        label='Confirmar Senha',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar Senha'})
    )

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError('As senhas não coincidem.')
        return password2

class AdminLoginForm(AuthenticationForm):
    """
    Formulário de login para o painel de administração.
    """
    username = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Senha'})
    )