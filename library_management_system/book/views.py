from django.shortcuts import render, get_object_or_404, redirect
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse
from django.db.models import F
from django.urls import reverse
from django.core.mail import send_mail
from django.conf import settings

from .models import Book, Review
from .constants import GENRE_CHOICES
from borrowings.constants import TRANSACTION_TYPE, BORROW, RETURN
from .forms import DepositForm, ReviewForm
from borrowings.models import Transaction

def index(request):
    if 'genre' in request.GET:
        genre = request.GET['genre']
        books = Book.objects.filter(category=genre)
    else:
        books = Book.objects.all()
    genres = GENRE_CHOICES
    return render(request, "book/index.html", {
        "book_list": books,
        "genres": genres,
    })

def details(request, book_id):
    book = get_object_or_404(Book, pk=book_id)
    reviews = Review.objects.filter(book=book).order_by("-timestamp")

    if request.method == "POST":
        if request.user.is_authenticated == False:
            return HttpResponse("You are not authorized for this action.")
        review_form = ReviewForm(request.POST, book=book, user=request.user)
        if review_form.is_valid():
            review_form.save()
            messages.success(request, message="Review posted successfully")
    else:
        review_form = ReviewForm(user=request.user, book=book)

    can_borrow = False
    why = ""

    if request.user.is_authenticated:
        try:
            borrow_count = Transaction.objects.filter(book=book, user=request.user, mode=BORROW).count()
            return_count = Transaction.objects.filter(book=book, user=request.user, mode=RETURN).count()
            if borrow_count > return_count:
                transaction = True
            else:
                transaction = None
        except Transaction.DoesNotExist:
            transaction = None
        
        if transaction is not None:
            why = "you already have borrowed a copy of this book and haven't returned yet"
        elif request.user.vault.balance < book.borrowing_price:
            why = "you don't have enough balance to borrow this book. Please deposit some money first"
        else:
            can_borrow = True

    return render(request, "book/details.html", {
        "book": book,
        "can_borrow": can_borrow,
        "why": why,
        "review_form": review_form,
        "reviews": reviews,
    })

@login_required
def deposit(request):
    if request.method == "POST":
        form = DepositForm(request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            vault = request.user.vault
            vault.balance = F("balance") + amount
            vault.save()
            mail_text = render_to_string("email/deposit.html", {
                "amount": amount,
                "user": request.user,
            })
            send_mail("Deposit Info - Library Management System", "", settings.EMAIL_HOST_USER, [request.user.email], 
                      html_message=mail_text)
            messages.success(request, message=f"Successfully Deposited {amount}")
            return redirect("index")
    else:
        form = DepositForm()
    return render(request, "book/deposit.html", {
        "form": form
    })

@login_required
def borrow(request):
    if request.method == "POST":
        book_id = int(request.POST['book_id'])
        book = get_object_or_404(Book, pk=book_id)
        can_borrow = False
        why = ""

        try:
            borrow_count = Transaction.objects.filter(book=book, user=request.user, mode=BORROW).count()
            return_count = Transaction.objects.filter(book=book, user=request.user, mode=RETURN).count()
            if borrow_count > return_count:
                transaction = True
            else:
                transaction = None
        except:
            transaction = None
        
        if transaction is not None:
            why = "you already have borrowed a copy of this book and haven't returned yet"
        elif request.user.vault.balance < book.borrowing_price:
            why = "you don't have enough balance to borrow this book. Please deposit some money first"
        else:
            can_borrow = True

        if not can_borrow:
            return HttpResponse(why)
        
        vault = request.user.vault
        vault.balance = vault.balance - book.borrowing_price
        vault.save()

        print(dir(vault))

        trx = Transaction.objects.create(
            user = request.user,
            book = book,
            mode = BORROW,
            balance_after_transaction = vault.balance,
        )

        mail_text = render_to_string("email/borrow.html", {
            "transaction": trx,
            "user": request.user,
        })
        send_mail("Borrow Info - Library Management System", "", settings.EMAIL_HOST_USER, [request.user.email], 
                    html_message=mail_text)

        messages.success(request, message="Successfully borrowed the book")
        return redirect(reverse("details", args=(book_id,)))
    
@login_required
def return_book(request):
    if request.method == "POST":
        book_id = request.POST["book_id"]
        try:
            last_transaction = Transaction.objects.filter(user=request.user, book__id=book_id).latest('timestamp')
        except Transaction.DoesNotExist:
            return HttpResponse("You cannot return a book that you didn't borrow (or borrowed and returned before)")
        if last_transaction.mode == RETURN:
            return HttpResponse("You cannot return a book that you didn't borrow (or borrowed and returned before)")
        book = get_object_or_404(Book, pk=book_id)
        vault = request.user.vault
        vault.balance += book.borrowing_price
        vault.save()

        Transaction.objects.create(
            user = request.user,
            book = book,
            mode = RETURN,
            balance_after_transaction = vault.balance,
        )

        messages.success(request, message=f"Successfully returned the book {book}")
        return redirect("profile")