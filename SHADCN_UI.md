# shadcn/ui Integration for Django

This project integrates the **exact look and feel** of shadcn/ui v4 components into Django templates using custom template tags and CSS.

## 🎨 **What You Get**

- **Exact shadcn/ui Design System** - Colors, typography, spacing, and components
- **Django Template Tags** - Easy-to-use template tags for all components
- **Responsive Design** - Mobile-first, accessible components
- **Dark Mode Ready** - Built-in dark mode support
- **Customizable** - Easy to extend and modify

## 🚀 **Quick Start**

### 1. Load the Template Tags

```html
{% load shadcn_ui %}
```

### 2. Use Components

```html
<!-- Button -->
{% button "Click Me" variant="primary" icon="plus" %}

<!-- Card -->
{% card title="My Card" description="Card description" content="<p>Card content</p>" %}

<!-- Input -->
{% input_field "name" label="Full Name" placeholder="Enter your name" required=True %}

<!-- Badge -->
{% badge "New" variant="default" %}

<!-- Table -->
{% table headers="Name,Email,Role" rows="[[\"John\",\"john@example.com\",\"Admin\"]]" %}
```

## 📦 **Available Components**

### Buttons
```html
{% button "Text" variant="primary|secondary|destructive|outline|ghost|link" size="sm|default|lg" icon="plus|calendar|edit|trash|save" %}
```

### Cards
```html
{% card title="Title" description="Description" content="<p>Content</p>" footer="<div>Footer</div>" %}
```

### Form Elements
```html
{% input_field "name" label="Label" placeholder="Placeholder" type="text|email|tel|date|time|textarea" required=True %}
```

### Badges
```html
{% badge "Text" variant="default|secondary|destructive|outline" %}
```

### Tables
```html
{% table headers="Col1,Col2,Col3" rows="[[\"Row1Col1\",\"Row1Col2\",\"Row1Col3\"],[\"Row2Col1\",\"Row2Col2\",\"Row2Col3\"]]" %}
```

### Alerts
```html
{% alert title="Alert Title" description="Alert description" variant="default|destructive" %}
```

### Navigation
```html
{% nav_link "Link Text" "/url/" active=True icon="calendar" %}
```

## 🎨 **Design System**

### Colors
- **Primary**: Blue (#3b82f6)
- **Secondary**: Gray (#f1f5f9)
- **Destructive**: Red (#ef4444)
- **Muted**: Light gray (#f8fafc)
- **Border**: Light gray (#e2e8f0)

### Typography
- **Font**: Inter (Google Fonts)
- **Sizes**: 0.75rem to 1.5rem
- **Weights**: 300, 400, 500, 600, 700

### Spacing
- **Padding**: 0.5rem to 1.5rem
- **Margins**: 0.25rem to 2rem
- **Gaps**: 0.5rem to 1rem

## 🔧 **Customization**

### 1. Modify Colors
Edit `static/css/shadcn-components.css`:

```css
:root {
  --primary: 221.2 83.2% 53.3%; /* Your primary color */
  --secondary: 210 40% 96%;     /* Your secondary color */
  /* ... other colors */
}
```

### 2. Add New Components
Create new template tags in `templates/templatetags/shadcn_ui.py`:

```python
@register.simple_tag
def my_component(text, **kwargs):
    context = {'text': text, **kwargs}
    return render_to_string('components/my_component.html', context)
```

### 3. Create Component Templates
Add new templates in `templates/components/`:

```html
<!-- templates/components/my_component.html -->
<div class="my-component {{ class }}">
    {{ text }}
</div>
```

## 📱 **Responsive Design**

All components are mobile-first and responsive:

```html
<!-- Responsive grid -->
<div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
    {% card title="Card 1" content="Content 1" %}
    {% card title="Card 2" content="Content 2" %}
    {% card title="Card 3" content="Content 3" %}
</div>
```

## 🌙 **Dark Mode**

Dark mode is built-in and can be toggled:

```html
<!-- Add dark class to body for dark mode -->
<body class="dark">
    <!-- Your content -->
</body>
```

## 🎯 **Examples**

### Dashboard Layout
```html
{% extends 'base.html' %}
{% load shadcn_ui %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8">
    <!-- Header -->
    <h1 class="text-3xl font-bold">Dashboard</h1>
    
    <!-- Stats Cards -->
    <div class="grid grid-cols-1 md:grid-cols-4 gap-6 my-8">
        {% card title="Total Users" content='<div class="text-2xl font-bold">1,234</div>' %}
        {% card title="Active Sessions" content='<div class="text-2xl font-bold">567</div>' %}
        {% card title="Revenue" content='<div class="text-2xl font-bold">$12,345</div>' %}
        {% card title="Growth" content='<div class="text-2xl font-bold">+12%</div>' %}
    </div>
    
    <!-- Actions -->
    <div class="flex gap-4">
        {% button "Create New" variant="primary" icon="plus" %}
        {% button "Export Data" variant="secondary" icon="save" %}
        {% button "Settings" variant="outline" icon="edit" %}
    </div>
</div>
{% endblock %}
```

### Form Layout
```html
{% card title="User Form" description="Create a new user account" content='<form class="space-y-6">{% csrf_token %}<div class="grid grid-cols-1 md:grid-cols-2 gap-4">{% input_field "first_name" label="First Name" required=True %}{% input_field "last_name" label="Last Name" required=True %}</div><div>{% input_field "email" label="Email" type="email" required=True %}</div><div>{% input_field "bio" label="Bio" type="textarea" placeholder="Tell us about yourself" %}</div><div class="flex justify-end space-x-4">{% button "Cancel" variant="outline" %}{% button "Save User" variant="primary" %}</div></form>' %}
```

## 🚀 **Demo Page**

Visit `/demo/` to see all components in action with live examples.

## 📚 **Resources**

- [shadcn/ui Documentation](https://ui.shadcn.com/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [Django Template Tags](https://docs.djangoproject.com/en/stable/howto/custom-template-tags/)

## 🤝 **Contributing**

1. Add new components to `templates/templatetags/shadcn_ui.py`
2. Create component templates in `templates/components/`
3. Add CSS styles to `static/css/shadcn-components.css`
4. Update this documentation

## 📄 **License**

This shadcn/ui integration is part of the Employee-Client Scheduling Service project.
