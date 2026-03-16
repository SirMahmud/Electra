from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages


def role_required(*roles):
    """Decorator to require specific user roles"""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                messages.error(request, 'Please login to access this page.')
                return redirect('accounts:login')
            
            if request.user.role not in roles:
                messages.error(
                    request,
                    f'You do not have permission to access this page.'
                )
                return redirect('home')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def voter_required(view_func):
    """Decorator to require voter role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.role != 'voter':
            messages.error(
                request,
                'This page is only accessible to voters.'
            )
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def admin_required(view_func):
    """Decorator to require admin or super_admin role"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.role not in ['admin', 'super_admin']:
            messages.error(
                request,
                'This page is only accessible to admins.'
            )
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper


def super_admin_required(view_func):
    """Decorator to require super_admin role only"""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please login to access this page.')
            return redirect('accounts:login')
        
        if request.user.role != 'super_admin':
            messages.error(
                request,
                'This page is only accessible to super admins.'
            )
            return redirect('home')
        
        return view_func(request, *args, **kwargs)
    return wrapper