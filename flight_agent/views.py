from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from .models import FlightSearchQuery, ChatMessage
from .flight_service import FlightAgentService
import json

User = get_user_model()


class FlightSearchView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            query = request.data.get('query', '')
            if not query:
                return Response(
                    {'error': 'Query is required'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save user message to chat history
            user_message = ChatMessage.objects.create(
                user=request.user,
                message=query,
                is_user=True
            )
            
            # Process query with flight agent
            flight_service = FlightAgentService()
            agent_response = flight_service.process_query(query)
            
            # Extract flight data if available
            flights_data = []
            origin = flight_service.extract_origin(query)
            destination = flight_service.extract_destination(query)
            date = flight_service.extract_date(query)
            
            # Get flight results
            flights = flight_service.search_flights(origin, destination, date)
            if flights and not flights[0].get('error'):
                flights_data = flights
                
                # Save search query to history
                FlightSearchQuery.objects.create(
                    user=request.user,
                    query=query,
                    origin=origin,
                    destination=destination,
                    date=date,
                    results=flights_data
                )
            
            # Save agent response to chat history
            agent_message = ChatMessage.objects.create(
                user=request.user,
                message=agent_response,
                is_user=False,
                flights=flights_data
            )
            
            return Response({
                'response': agent_response,
                'flights': flights_data,
                'message_id': agent_message.id
            })
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChatHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            messages = ChatMessage.objects.filter(user=request.user)[:50]
            messages_data = []
            
            for message in messages:
                messages_data.append({
                    'id': message.id,
                    'message': message.message,
                    'is_user': message.is_user,
                    'flights': message.flights,
                    'timestamp': message.timestamp.isoformat()
                })
            
            return Response({'messages': messages_data})
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def delete(self, request):
        try:
            ChatMessage.objects.filter(user=request.user).delete()
            return Response({'message': 'Chat history cleared'})
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SearchHistoryView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        try:
            searches = FlightSearchQuery.objects.filter(user=request.user)[:20]
            searches_data = []
            
            for search in searches:
                searches_data.append({
                    'id': search.id,
                    'query': search.query,
                    'origin': search.origin,
                    'destination': search.destination,
                    'date': search.date,
                    'results': search.results,
                    'timestamp': search.timestamp.isoformat()
                })
            
            return Response({'searches': searches_data})
            
        except Exception as e:
            return Response(
                {'error': f'Internal server error: {str(e)}'}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
