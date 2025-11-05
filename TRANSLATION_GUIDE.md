# Guide de Traduction - Ken Project

## Configuration

Le projet supporte l'anglais (EN) et le français (FR) avec Django i18n.

## Comment ajouter des traductions dans un nouveau template

### 1. Charger le module i18n

En haut de votre template, ajoutez:
```django
{% load i18n %}
```

### 2. Traduire du texte simple

Pour du texte sans variables:
```django
<h1>{% trans "Welcome to Ken" %}</h1>
<button>{% trans "Sign Up" %}</button>
```

### 3. Traduire du texte avec variables

Pour du texte contenant des variables Django:
```django
{% blocktrans with name=user.username %}
    Welcome back, {{ name }}!
{% endblocktrans %}
```

Ou avec plusieurs variables:
```django
{% blocktrans with points=profile.total_points balance=profile.available_balance_usd %}
    You have {{ points }} points worth ${{ balance }}
{% endblocktrans %}
```

### 4. NE PAS traduire

- URLs: `{% url 'dashboard' %}`
- Classes CSS: `class="bg-primary"`
- IDs: `id="myElement"`
- Noms de variables
- Code JavaScript

## Ajouter de nouvelles traductions

### 1. Ajouter le texte dans le template
```django
<p>{% trans "New text to translate" %}</p>
```

### 2. Ajouter la traduction dans le fichier .po

Ouvrez `/locale/fr/LC_MESSAGES/django.po` et ajoutez:
```
msgid "New text to translate"
msgstr "Nouveau texte à traduire"
```

### 3. Compilez les traductions (optionnel pour dev)

```bash
python manage.py compilemessages --ignore=env
```

Note: En développement avec DEBUG=True, Django recharge automatiquement les fichiers .po

## Structure des fichiers

```
project/
├── locale/
│   └── fr/
│       └── LC_MESSAGES/
│           ├── django.po       # Fichier de traduction (éditable)
│           └── django.mo       # Fichier compilé (auto-généré)
├── core/
│   └── templates/
│       └── core/
│           ├── language_switcher.html  # Sélecteur de langue
│           └── *.html                  # Tous les templates
└── ken_project/
    └── settings.py  # Configuration i18n
```

## Exemples pratiques

### Template de base
```django
{% load i18n %}
<!DOCTYPE html>
<html lang="{% get_current_language as LANGUAGE_CODE %}{{ LANGUAGE_CODE }}">
<head>
    <title>{% trans "My Page Title" %}</title>
</head>
<body>
    <h1>{% trans "Welcome" %}</h1>
    
    {% blocktrans with user=request.user.username %}
        Hello {{ user }}
    {% endblocktrans %}
    
    <a href="{% url 'dashboard' %}">{% trans "Dashboard" %}</a>
</body>
</html>
```

### Formulaire
```django
{% load i18n %}
<form method="post">
    {% csrf_token %}
    <label>{% trans "Username" %}</label>
    <input type="text" name="username" placeholder="{% trans "Enter username" %}">
    
    <label>{% trans "Password" %}</label>
    <input type="password" name="password">
    
    <button type="submit">{% trans "Login" %}</button>
</form>
```

### Messages avec variables
```django
{% load i18n %}
{% blocktrans count counter=items|length %}
    You have {{ counter }} item
{% plural %}
    You have {{ counter }} items
{% endblocktrans %}
```

## Changer de langue

Le sélecteur de langue est inclus dans tous les templates via:
```django
{% include 'core/language_switcher.html' %}
```

Les utilisateurs peuvent cliquer sur EN ou FR pour changer de langue.

## Maintenance

### Trouver les textes non traduits

Cherchez dans les templates:
```bash
grep -r ">[A-Z]" core/templates/ | grep -v "{% trans"
```

### Vérifier les fichiers .po

Assurez-vous que tous les `msgid` ont un `msgstr` correspondant.

## Ressources

- [Documentation Django i18n](https://docs.djangoproject.com/en/5.1/topics/i18n/)
- [Template tags i18n](https://docs.djangoproject.com/en/5.1/topics/i18n/translation/#internationalization-in-template-code)
